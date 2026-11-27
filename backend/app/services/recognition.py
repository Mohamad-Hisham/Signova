"""Bound sample windows, inference and candidate ownership per capture stream."""

import asyncio
import math
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import TypeVar

from app.models.base import (
    AdapterRegistry,
    ModelAdapter,
    Prediction,
    validate_prediction,
)
from app.services.word_gate import WordGate, WordGateState
from app.utilities.ids import new_uuid
from app.utilities.time import Clock

Result = TypeVar("Result")


class StaleStreamError(Exception):
    pass


class CandidateUnavailableError(StaleStreamError):
    pass


class StaleFrameError(Exception):
    pass


class FrameGapError(Exception):
    pass


class RateLimitError(Exception):
    pass


class OverloadedError(Exception):
    pass


class InsufficientRateError(Exception):
    pass


class InferenceTimeoutError(Exception):
    pass


@dataclass(frozen=True)
class PendingFrame:
    capture_ms: float
    load_jpeg: Callable[[], bytes]


@dataclass
class StreamState:
    stream_id: str
    mode: str
    adapter: ModelAdapter
    gate: WordGate
    window_samples: int
    required_sample_fps: float | None
    next_frame_seq: int = 1
    last_capture_ms: float | None = None
    last_arrival: float | None = None
    arrivals: deque[float] = field(default_factory=deque)
    frames: list[bytes] = field(default_factory=list)
    times_ms: list[float] = field(default_factory=list)
    pending_frame: PendingFrame | None = None
    generation: int = 0
    inference_active: bool = False
    needs_reset: bool = True
    preview: Prediction | None = None
    candidate_id: str | None = None
    preview_deadline: float = 0.0

    def clear_preview(self) -> None:
        self.preview = None
        self.candidate_id = None
        self.preview_deadline = 0.0

    def break_continuity(self) -> None:
        self.frames.clear()
        self.times_ms.clear()
        self.pending_frame = None
        self.gate.break_continuity()
        self.clear_preview()
        self.generation += 1
        self.needs_reset = True


class RecognitionService:
    def __init__(
        self,
        clock: Clock,
        adapters: AdapterRegistry | Mapping[str, ModelAdapter],
        *,
        max_window_samples: int = 60,
        candidate_ttl_seconds: float = 2.0,
        continuity_gap_ms: int = 500,
        entry_score: float = 0.85,
        exit_score: float = 0.65,
        stability_seconds: float = 0.300,
        neutral_dwell_seconds: float = 0.300,
        minimum_observations: int = 3,
        inference_timeout_seconds: float = 2.0,
        max_inferences: int = 1,
    ):
        self.clock = clock
        self.adapters = adapters
        self.max_window_samples = max_window_samples
        self.candidate_ttl_seconds = candidate_ttl_seconds
        self.continuity_gap_ms = continuity_gap_ms
        self.entry_score = entry_score
        self.exit_score = exit_score
        self.stability_seconds = stability_seconds
        self.neutral_dwell_seconds = neutral_dwell_seconds
        self.minimum_observations = minimum_observations
        self.inference_timeout_seconds = inference_timeout_seconds
        self.max_inferences = max_inferences
        self.streams: dict[str, StreamState] = {}
        self._inferences: set[asyncio.Task] = set()

    def start_stream(self, mode: str) -> StreamState:
        if isinstance(self.adapters, AdapterRegistry):
            adapter = self.adapters.get(mode)
        else:
            adapter = self.adapters[mode]
        window_samples = getattr(adapter, "window_samples", 1)
        if (
            type(window_samples) is not int
            or not 1 <= window_samples <= self.max_window_samples
        ):
            raise ValueError("The recognition window is outside server limits")

        state = StreamState(
            stream_id=new_uuid(),
            mode=mode,
            adapter=adapter,
            gate=WordGate(
                self.clock,
                entry_score=self.entry_score,
                exit_score=self.exit_score,
                stability_seconds=self.stability_seconds,
                neutral_dwell_seconds=self.neutral_dwell_seconds,
                minimum_observations=self.minimum_observations,
                candidate_freshness_seconds=self.candidate_ttl_seconds,
            ),
            window_samples=window_samples,
            required_sample_fps=getattr(adapter, "required_sample_fps", None),
        )
        self.streams[state.stream_id] = state
        return state

    def invalidate_stream(self, stream_id: str) -> None:
        state = self.streams.pop(stream_id, None)
        if state is not None:
            state.break_continuity()

    def break_continuity(self, stream_id: str) -> None:
        state = self.streams.get(stream_id)
        if state is not None:
            state.break_continuity()

    async def shutdown(self) -> None:
        for stream_id in list(self.streams):
            self.invalidate_stream(stream_id)
        await asyncio.gather(*self._inferences, return_exceptions=True)

    def admit_frame(
        self,
        stream_id: str,
        frame_seq: int,
        capture_ms: float,
        load_jpeg: Callable[[], bytes],
        *,
        max_fps: int,
    ) -> None:
        state = self.streams.get(stream_id)
        if state is None:
            raise StaleStreamError
        if not math.isfinite(capture_ms) or capture_ms < 0:
            raise StaleFrameError
        if frame_seq != state.next_frame_seq or (
            state.last_capture_ms is not None and capture_ms <= state.last_capture_ms
        ):
            state.next_frame_seq = max(state.next_frame_seq, frame_seq + 1)
            state.break_continuity()
            raise StaleFrameError

        state.next_frame_seq = frame_seq + 1
        now = self.clock.now_monotonic()
        capture_gap = (
            state.last_capture_ms is not None
            and capture_ms - state.last_capture_ms > self.continuity_gap_ms
        )
        arrival_gap = (
            state.last_arrival is not None
            and (now - state.last_arrival) * 1000 > self.continuity_gap_ms
        )
        state.last_capture_ms = capture_ms
        state.last_arrival = now
        if state.inference_active or state.pending_frame is not None:
            state.break_continuity()
            raise OverloadedError
        if capture_gap or arrival_gap:
            state.break_continuity()
            raise FrameGapError

        while state.arrivals and now - state.arrivals[0] >= 1:
            state.arrivals.popleft()
        if len(state.arrivals) >= max_fps:
            state.break_continuity()
            raise RateLimitError
        state.arrivals.append(now)
        state.pending_frame = PendingFrame(capture_ms, load_jpeg)

    async def process_admitted_frame(
        self, stream_id: str, *, on_admitted: Callable[[], None] | None = None
    ) -> None:
        state = self.streams.get(stream_id)
        if state is None:
            raise StaleStreamError
        pending = state.pending_frame
        if pending is None or state.inference_active:
            raise OverloadedError
        state.pending_frame = None
        if len(self._inferences) >= self.max_inferences:
            state.break_continuity()
            raise OverloadedError

        state.inference_active = True
        generation = state.generation
        frames = [*state.frames]
        times_ms = [*state.times_ms, pending.capture_ms][-state.window_samples :]
        task = asyncio.create_task(
            asyncio.to_thread(
                self._infer, state, pending, frames, times_ms, state.needs_reset
            )
        )
        self._inferences.add(task)
        task.add_done_callback(self._inference_finished)
        try:
            frames, prediction = await asyncio.wait_for(
                asyncio.shield(task), timeout=self.inference_timeout_seconds
            )
        except TimeoutError:
            state.break_continuity()
            raise InferenceTimeoutError from None
        except Exception:
            state.break_continuity()
            raise
        finally:
            state.inference_active = False

        if self.streams.get(stream_id) is not state:
            raise StaleStreamError
        if state.generation != generation:
            raise FrameGapError
        if on_admitted is not None:
            on_admitted()
        state.frames = frames
        state.times_ms = times_ms
        state.needs_reset = False
        self._update_preview(state, prediction)

    @staticmethod
    def _infer(
        state: StreamState,
        pending: PendingFrame,
        frames: list[bytes],
        times_ms: list[float],
        reset_adapter: bool,
    ) -> tuple[list[bytes], Prediction | None]:
        frames = [*frames, pending.load_jpeg()][-state.window_samples :]
        if reset_adapter:
            state.adapter.reset_stream(state.stream_id)
        if len(frames) < state.window_samples:
            return frames, None
        if state.required_sample_fps is not None and len(times_ms) > 1:
            span_ms = times_ms[-1] - times_ms[0]
            sample_fps = 1000 * (len(times_ms) - 1) / span_ms
            if sample_fps + 1e-9 < state.required_sample_fps:
                raise InsufficientRateError
        prediction = validate_prediction(state.adapter.predict(frames, times_ms))
        if prediction.model_version != state.adapter.model_version:
            raise ValueError("Recognition returned evidence for a different model")
        return frames, prediction

    def _inference_finished(self, task: asyncio.Task) -> None:
        self._inferences.discard(task)
        if not task.cancelled():
            task.exception()

    def _update_preview(
        self, state: StreamState, prediction: Prediction | None
    ) -> None:
        previous = self._current_preview(state)
        eligible = state.gate.update(prediction)
        if (
            prediction is None
            or not prediction.usable
            or prediction.neutral
            or state.gate.state in (WordGateState.LOCKED, WordGateState.WAIT_RELEASE)
        ):
            state.clear_preview()
            return
        if previous is None or previous.label_id != prediction.label_id:
            state.candidate_id = new_uuid()
        state.preview = eligible or prediction
        state.preview_deadline = self.clock.deadline(self.candidate_ttl_seconds)

    def _current_preview(self, state: StreamState) -> Prediction | None:
        if self.clock.expired(state.preview_deadline):
            state.clear_preview()
        return state.preview

    def candidate_view(self, stream_id: str) -> dict | None:
        state = self.streams.get(stream_id)
        if state is None:
            return None
        preview = self._current_preview(state)
        if preview is None:
            return None
        eligible = state.gate.eligible_candidate() is not None
        return {
            "candidate_id": state.candidate_id,
            "stream_id": stream_id,
            "mode": state.mode,
            "label_id": preview.label_id,
            "text": preview.text,
            "score": preview.score,
            "stable": eligible,
            "eligible": eligible,
            "expires_in_ms": max(
                0,
                math.ceil((state.preview_deadline - self.clock.now_monotonic()) * 1000),
            ),
            "model_version": preview.model_version,
        }

    def current_candidate(self, stream_id: str) -> tuple[str, Prediction] | None:
        state = self.streams.get(stream_id)
        if state is None or self._current_preview(state) is None:
            return None
        eligible = state.gate.eligible_candidate()
        if eligible is None or state.candidate_id is None:
            return None
        return state.candidate_id, eligible

    def commit_candidate(
        self,
        stream_id: str,
        candidate_id: str,
        operation: Callable[[Prediction], Result],
    ) -> Result:
        state = self.streams.get(stream_id)
        if state is None:
            raise StaleStreamError
        current = self.current_candidate(stream_id)
        if current is None or current[0] != candidate_id:
            raise CandidateUnavailableError
        result = operation(current[1])
        state.gate.lock_segment()
        state.clear_preview()
        return result

    def consume_candidate(self, stream_id: str, candidate_id: str) -> Prediction:
        return self.commit_candidate(
            stream_id, candidate_id, lambda prediction: prediction
        )
