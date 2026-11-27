from collections import deque

import pytest

from app.services.rate_limits import CreationRateLimiter, take_request
from app.services.sessions import SessionExpired, SessionNotFound, SessionStore
from app.utilities.time import Clock


def test_earliest_reconnect_and_absolute_deadlines():
    now = [0.0]
    terminal = []
    store = SessionStore(
        Clock(lambda: now[0]),
        absolute_timeout_seconds=20,
        on_terminate=lambda record, reason: terminal.append(
            (record.session_id, reason)
        ),
    )
    dropped, token = store.create("alphabet", model_version="a")
    dropped.reconnect_deadline = 5
    ended, _ = store.create("word", model_version="w")
    store.mark_ended(ended)
    now[0] = 5
    with pytest.raises(SessionNotFound):
        store.authenticate(dropped.session_id, "wrong")
    assert terminal == []
    with pytest.raises(SessionExpired):
        store.authenticate(dropped.session_id, token)
    assert terminal == [(dropped.session_id, "reconnect_timeout")]
    now[0] = 20
    assert store.sweep_expired() == 1
    assert terminal[-1] == (ended.session_id, "absolute")


def test_termination_erases_content_caches_and_stream_after_terminal_callback():
    observed = []
    store = SessionStore(
        Clock(lambda: 0),
        on_terminate=lambda record, reason: observed.append((record.stream_id, reason)),
    )
    record, _ = store.create("alphabet", model_version="a", recovery_enabled=True)
    record.items.append({"text": "س"})
    record.stream_id = "test-stream"
    record.socket_id = "test-socket"
    record.command_cache.execute("command", "fingerprint", lambda: {"text": "س"})
    record.mutation_times.append(0)
    store.delete(record)
    assert observed == [("test-stream", "user")]
    assert record.items == [] and not record.mutation_times
    assert (
        record.stream_id is None
        and record.socket_id is None
        and not record.recovery_enabled
    )
    assert record.command_cache.execute("command", "fingerprint", lambda: None) is None


def test_bounded_tombstones_and_shutdown_drop_current_records():
    store = SessionStore(Clock(lambda: 0), max_tombstones=1)
    removed, secret = store.create("word", model_version="w")
    store.delete(removed)
    newer, _ = store.create("alphabet", model_version="a")
    store.delete(newer)
    with pytest.raises(SessionNotFound):
        store.authenticate(removed.session_id, secret)
    active, active_secret = store.create("word", model_version="w")
    store.shutdown()
    with pytest.raises(SessionNotFound):
        store.authenticate(active.session_id, active_secret)


def test_rate_window_bounds_sources_and_rounds_retry_after():
    now = [0.25]
    limiter = CreationRateLimiter(Clock(lambda: now[0]), 1, max_sources=1)
    assert limiter.take("first") is None
    assert limiter.take("first") == 60
    now[0] = 59.5
    assert limiter.take("second") == 1
    now[0] = 60.25
    assert limiter.take("second") is None
    times = deque([0.25])
    assert take_request(times, 59.9, 1) == 1
    assert take_request(times, 60.25, 1) is None
