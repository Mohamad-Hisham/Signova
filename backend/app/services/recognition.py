# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve bounded sample admission, model routing and current candidate/segment
#   orchestration.
# Owner: Basel.
# Expected inputs: Validated ordered JPEGs, current session/stream, approved adapter evidence
#   and capture controls.
# Expected outputs: Future frame acknowledgements, current candidate eligibility and authorized
#   commit intentions.
# Responsibilities: Build owner windows, schedule outside locks, recheck stream/session/capture,
#   enforce hold latch and reset all pending evidence on interruption.
# Connections: Session/transcript/command services, word_gate.py, dedicated model adapters and
#   WS writer.
# Future implementation: Implement cancellation-aware bounded inference and per-stream resource
#   ownership.
# Rules and limitations: Pause never flushes classification; no stale result revival, offline
#   backlog, duplicate artificial frames or fake/model training.
# Expected tests or acceptance: Long gap/overflow/out-of-order resets window; held letters/words
#   once, deliberate new segments repeat; timeout retains native capacity slot.

import math
from dataclasses import dataclass, field

from app.models.base import ModelAdapter, Prediction
from app.utilities.ids import new_uuid
from app.utilities.time import Clock


class StaleStreamError(Exception):
    pass


class StaleFrameError(Exception):
    pass


class OverloadedError(Exception):
    pass


@dataclass
class StreamState:
    stream_id: str
    next_frame_seq: int = 1
    last_capture_ms: float | None = None
    frames: list[bytes] = field(default_factory=list)
    times_ms: list[float] = field(default_factory=list)
    pending_frame: tuple[int, bytes, float] | None = None
    candidate: Prediction | None = None
    candidate_id: str | None = None
    candidate_deadline: float = 0
    in_flight: bool = False


class RecognitionService:
    def __init__(
        self,
        clock: Clock,
        adapters: dict[str, ModelAdapter],
        *,
        max_window_samples: int = 60,
        candidate_ttl_seconds: float = 2.0,
        continuity_gap_ms: float = 500,
    ):
        self.clock = clock
        self.adapters = adapters
        self.max_window_samples = max_window_samples
        self.candidate_ttl_seconds = candidate_ttl_seconds
        self.continuity_gap_ms = continuity_gap_ms
        self.streams: dict[str, StreamState] = {}

    def start_stream(self, mode: str) -> StreamState:
        if mode not in self.adapters:
            raise KeyError("Recognition adapter is unavailable")

        state = StreamState(stream_id=new_uuid())
        self.streams[state.stream_id] = state
        adapter = self.adapters[mode]
        adapter.reset_stream(state.stream_id)
        return state

    def invalidate_stream(self, stream_id: str) -> None:
        state = self.streams.pop(stream_id, None)
        if state is None:
            return
        state.pending_frame = None
        state.candidate = None
        state.candidate_id = None
        state.in_flight = False

    def admit_frame(
        self,
        stream_id: str,
        frame_seq: int,
        capture_ms: float,
        jpeg_bytes: bytes,
    ) -> tuple[str, int]:
        state = self.streams.get(stream_id)
        if state is None:
            raise StaleStreamError
        if state.in_flight or state.pending_frame is not None:
            raise OverloadedError
        if frame_seq != state.next_frame_seq:
            raise StaleFrameError
        if not math.isfinite(capture_ms) or capture_ms < 0:
            raise ValueError("capture_ms must be finite and nonnegative")

        if (
            state.last_capture_ms is not None
            and capture_ms - state.last_capture_ms > self.continuity_gap_ms
        ):
            state.frames.clear()
            state.times_ms.clear()
            state.candidate = None
            state.candidate_id = None

        state.pending_frame = (frame_seq, jpeg_bytes, capture_ms)
        state.in_flight = True
        return state.stream_id, frame_seq

    def process_admitted_frame(
        self,
        mode: str,
        stream_id: str,
    ) -> Prediction | None:
        state = self.streams.get(stream_id)
        if state is None:
            raise StaleStreamError
        if state.pending_frame is None:
            raise OverloadedError

        frame_seq, jpeg_bytes, capture_ms = state.pending_frame
        state.pending_frame = None
        state.in_flight = False
        state.frames.append(jpeg_bytes)
        state.times_ms.append(capture_ms)
        state.last_capture_ms = capture_ms
        state.next_frame_seq = frame_seq + 1

        if len(state.frames) > self.max_window_samples:
            state.frames = state.frames[-self.max_window_samples :]
            state.times_ms = state.times_ms[-self.max_window_samples :]

        adapter = self.adapters[mode]
        prediction = adapter.predict(state.frames, state.times_ms)

        if not prediction.usable:
            state.candidate = None
            state.candidate_id = None
            state.candidate_deadline = 0
            return None

        state.candidate = prediction
        state.candidate_id = new_uuid()
        state.candidate_deadline = self.clock.deadline(self.candidate_ttl_seconds)
        return prediction

    def current_candidate(self, stream_id: str) -> tuple[str, Prediction] | None:
        state = self.streams.get(stream_id)
        if state is None or state.candidate is None:
            return None
        if self.clock.expired(state.candidate_deadline):
            state.candidate = None
            state.candidate_id = None
            state.candidate_deadline = 0
            return None
        return state.candidate_id, state.candidate

    def consume_candidate(
        self,
        stream_id: str,
        candidate_id: str,
    ) -> Prediction:
        current = self.current_candidate(stream_id)
        if current is None:
            raise StaleStreamError
        current_id, prediction = current
        if current_id != candidate_id:
            raise StaleStreamError

        state = self.streams[stream_id]
        state.candidate = None
        state.candidate_id = None
        state.candidate_deadline = 0
        return prediction
