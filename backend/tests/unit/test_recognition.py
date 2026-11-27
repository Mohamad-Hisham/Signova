import asyncio
import threading

import pytest

from app.models.base import Prediction
from app.services.recognition import (
    CandidateUnavailableError,
    FrameGapError,
    InferenceTimeoutError,
    InsufficientRateError,
    OverloadedError,
    RateLimitError,
    RecognitionService,
    StaleFrameError,
    StaleStreamError,
)
from app.utilities.time import Clock


class TestTime:
    __test__ = False

    def __init__(self):
        self.now = 10.0
        self.clock = Clock(lambda: self.now)

    def advance(self, seconds):
        self.now += seconds


class StubAdapter:
    mode = "alphabet"
    model_version = "unit-test-v1"

    def __init__(self, *, window_samples=1, required_sample_fps=None):
        self.window_samples = window_samples
        self.required_sample_fps = required_sample_fps
        self.prediction = Prediction(
            "alef", "أ", 0.95, False, True, model_version=self.model_version
        )
        self.windows = []
        self.resets = []

    def reset_stream(self, stream_id):
        self.resets.append(stream_id)

    def predict(self, frames, times_ms):
        self.windows.append((frames, times_ms))
        return self.prediction


async def process(service, stream, seq, capture_ms, payload=b"sample", max_fps=10):
    service.admit_frame(
        stream.stream_id, seq, capture_ms, lambda: payload, max_fps=max_fps
    )
    await service.process_admitted_frame(stream.stream_id)


@pytest.mark.asyncio
async def test_preview_stability_confirmation_and_release():
    time = TestTime()
    adapter = StubAdapter()
    service = RecognitionService(time.clock, {"alphabet": adapter})
    stream_id = None
    for seq in range(1, 5):
        if seq == 1:
            stream = service.start_stream("alphabet")
            stream_id = stream.stream_id
        await process(service, stream, seq, seq * 110)
        candidate = service.candidate_view(stream_id)
        if seq == 1:
            candidate_id = candidate["candidate_id"]
        assert candidate["candidate_id"] == candidate_id
        assert candidate["eligible"] == (seq == 4)
        assert candidate["stable"] == (seq == 4)
        time.advance(0.11)

    def fail_append(prediction):
        assert prediction.text == "أ"
        raise RuntimeError("write failed")

    with pytest.raises(RuntimeError, match="write failed"):
        service.commit_candidate(stream_id, candidate_id, fail_append)
    assert service.current_candidate(stream_id)[0] == candidate_id
    assert (
        service.commit_candidate(
            stream_id, candidate_id, lambda prediction: prediction.label_id
        )
        == "alef"
    )
    with pytest.raises(CandidateUnavailableError):
        service.consume_candidate(stream_id, candidate_id)

    # Rejected inputs and switching directly to another label cannot release a commit.
    adapter.prediction = Prediction(
        None, None, 0.0, False, False, model_version=adapter.model_version
    )
    await process(service, stream, 5, 550)
    time.advance(0.11)
    adapter.prediction = Prediction(
        "baa", "ب", 0.97, False, True, model_version=adapter.model_version
    )
    await process(service, stream, 6, 660)
    assert service.candidate_view(stream_id) is None
    time.advance(0.11)

    # Evaluated neutral evidence is deliberately separate from unusable predictions.
    adapter.prediction = Prediction(
        None, None, 0.99, True, False, model_version=adapter.model_version
    )
    for seq in range(7, 11):
        await process(service, stream, seq, seq * 110)
        assert service.candidate_view(stream_id) is None
        time.advance(0.11)

    adapter.prediction = Prediction(
        "alef", "أ", 0.95, False, True, model_version=adapter.model_version
    )
    time.advance(0.11)
    await process(service, stream, 11, 1210)
    assert service.candidate_view(stream_id)["candidate_id"] != candidate_id


@pytest.mark.asyncio
async def test_temporal_window_counts_and_enforces_sampling_rate():
    time = TestTime()
    adapter = StubAdapter(window_samples=3, required_sample_fps=5)
    service = RecognitionService(time.clock, {"word": adapter})
    stream = service.start_stream("word")
    for seq in range(1, 5):
        await process(service, stream, seq, seq * 100, bytes([seq]))
        time.advance(0.10)
    assert adapter.windows == [
        ([b"\x01", b"\x02", b"\x03"], [100, 200, 300]),
        ([b"\x02", b"\x03", b"\x04"], [200, 300, 400]),
    ]
    assert adapter.resets == [stream.stream_id]

    too_slow = service.start_stream("word")
    await process(service, too_slow, 1, 100)
    time.advance(0.25)
    await process(service, too_slow, 2, 350)
    time.advance(0.25)
    with pytest.raises(InsufficientRateError):
        await process(service, too_slow, 3, 600)
    assert not too_slow.frames
    assert len(adapter.windows) == 2


@pytest.mark.asyncio
async def test_stream_sequence_rate_gap_and_candidate_timeout():
    time = TestTime()
    adapter = StubAdapter()
    service = RecognitionService(
        time.clock, {"alphabet": adapter}, minimum_observations=1, stability_seconds=0
    )
    stream = service.start_stream("alphabet")
    await process(service, stream, 1, 100, max_fps=1)
    candidate_id = service.candidate_view(stream.stream_id)["candidate_id"]
    with pytest.raises(StaleFrameError):
        await process(service, stream, 1, 100, max_fps=1)
    assert service.current_candidate(stream.stream_id) is None
    with pytest.raises(RateLimitError):
        await process(service, stream, 2, 200, max_fps=1)
    time.advance(1.1)
    with pytest.raises(FrameGapError):
        await process(service, stream, 3, 1300, max_fps=1)
    time.advance(0.1)
    await process(service, stream, 4, 1400, max_fps=1)
    replacement = service.candidate_view(stream.stream_id)["candidate_id"]
    assert replacement != candidate_id

    time.advance(2.1)
    assert service.candidate_view(stream.stream_id) is None
    assert service.current_candidate(stream.stream_id) is None
    service.invalidate_stream(stream.stream_id)
    with pytest.raises(StaleStreamError):
        await process(service, stream, 5, 1500)
    assert stream.frames == []


@pytest.mark.asyncio
async def test_inference_timeout_keeps_native_slot_until_completion():
    clock = Clock()
    adapter = StubAdapter()
    service = RecognitionService(
        clock, {"alphabet": adapter}, inference_timeout_seconds=0.10, max_inferences=1
    )
    started = threading.Event()
    release = threading.Event()
    old_predict = adapter.predict

    def slow_prediction(frames, times_ms):
        started.set()
        release.wait(1)
        return old_predict(frames, times_ms)

    adapter.predict = slow_prediction
    first = service.start_stream("alphabet")
    second = service.start_stream("alphabet")
    try:
        with pytest.raises(InferenceTimeoutError):
            await process(service, first, 1, 100)
        assert started.is_set()
        assert not release.is_set()
        with pytest.raises(OverloadedError):
            await process(service, second, 1, 100)
        assert service.candidate_view(first.stream_id) is None
    finally:
        release.set()
        await asyncio.wait_for(service.shutdown(), timeout=2)
    assert not service.streams
    assert len(adapter.windows) == 1


@pytest.mark.asyncio
async def test_late_result_is_discarded_when_stream_is_replaced():
    adapter = StubAdapter()
    service = RecognitionService(Clock(), {"alphabet": adapter})
    started = threading.Event()
    release = threading.Event()

    def prediction_after_release(frames, times_ms):
        started.set()
        release.wait(1)
        return adapter.prediction

    adapter.predict = prediction_after_release
    stream = service.start_stream("alphabet")
    task = asyncio.create_task(process(service, stream, 1, 100))
    try:
        assert await asyncio.to_thread(started.wait, 1)
        service.invalidate_stream(stream.stream_id)
        replacement = service.start_stream("alphabet")
    finally:
        release.set()
    with pytest.raises(StaleStreamError):
        await task
    assert service.candidate_view(stream.stream_id) is None
    assert service.candidate_view(replacement.stream_id) is None
    assert not stream.frames
