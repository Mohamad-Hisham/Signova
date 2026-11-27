import asyncio
import base64
import json
import threading
from contextlib import asynccontextmanager
from io import BytesIO
from uuid import uuid4

import pytest
from anyio import CancelScope
from httpx import ASGITransport, AsyncClient
from PIL import Image

from app.config import LOCAL_ALPHABET_CHECKPOINT, LOCAL_ALPHABET_HAND_MODEL, Settings
from app.main import create_app
from app.models.base import Prediction
from app.schemas.common import Candidate
from app.schemas.events import ServerEnvelope
from app.utilities.time import Clock

ORIGIN = "http://localhost:5173"


class LiveTestSocket:
    def __init__(self, app, session_id, origin=ORIGIN):
        self.app = app
        self.path = f"/api/v1/ws/sessions/{session_id}"
        self.origin = origin
        self.to_server = asyncio.Queue()
        self.from_server = asyncio.Queue()

    async def __aenter__(self):
        headers = [] if self.origin is None else [(b"origin", self.origin.encode())]
        scope = {
            "type": "websocket",
            "asgi": {"version": "3.0", "spec_version": "2.4"},
            "scheme": "ws",
            "path": self.path,
            "raw_path": self.path.encode(),
            "root_path": "",
            "query_string": b"",
            "headers": headers,
            "server": ("testserver", 80),
            "client": ("testclient", 12345),
            "subprotocols": [],
        }
        self.task = asyncio.create_task(self.run(scope))
        await self.to_server.put({"type": "websocket.connect"})
        return self

    async def run(self, scope):
        with CancelScope() as cancel_scope:
            self.cancel_scope = cancel_scope
            await self.app(scope, self.to_server.get, self.from_server.put)

    async def __aexit__(self, _error_type, _error, _traceback):
        if not self.task.done():
            await self.to_server.put({"type": "websocket.disconnect", "code": 1000})
        await asyncio.wait_for(self.task, timeout=3)

    async def send(self, value):
        await self.send_raw(text=json.dumps({"protocol_version": 1, **value}))

    async def send_raw(self, **payload):
        await self.to_server.put({"type": "websocket.receive", **payload})

    async def receive(self):
        return await asyncio.wait_for(self.from_server.get(), timeout=3)

    async def expect_accept(self):
        assert (await self.receive())["type"] == "websocket.accept"

    async def event(self, event_type):
        output = await self.receive()
        assert output["type"] == "websocket.send"
        event = ServerEnvelope.model_validate_json(output["text"])
        assert event.type == event_type
        assert event.session_id == self.path.rsplit("/", 1)[-1]
        return event

    async def expect_close(self, code):
        message = await self.receive()
        assert message["type"] == "websocket.close"
        assert message["code"] == code


class StaticAdapter:
    window_samples = 1
    required_sample_fps = None

    def __init__(self, mode, label_id, text):
        self.mode = mode
        self.model_version = f"{mode}-socket-test"
        self.prediction = Prediction(
            label_id, text, 0.97, False, True, model_version=self.model_version
        )
        self.samples = []

    def reset_stream(self, stream_id):
        pass

    def predict(self, frames, times_ms):
        self.samples.append((frames, times_ms))
        return self.prediction


@pytest.fixture
def app_and_time():
    now = [10.0]
    app = create_app(Settings(), clock=Clock(lambda: now[0]), load_models=False)
    app.state.adapter_registry.register(
        "alphabet", StaticAdapter("alphabet", "alef", "أ")
    )
    app.state.adapter_registry.register("word", StaticAdapter("word", "water", "ماء"))
    return app, now


@pytest.fixture
def jpeg_data():
    with BytesIO() as buffer:
        Image.new("RGB", (8, 6), color=(30, 40, 50)).save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode()


@asynccontextmanager
async def client_and_session(app, mode="alphabet"):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/sessions", json={"mode": mode})
        assert response.status_code == 201
        body = response.json()
        yield client, body["session"]["session_id"], body["session_token"]


def authorization(token):
    return {"Authorization": f"Bearer {token}"}


async def live_auth(socket, token):
    await socket.expect_accept()
    await socket.send({"type": "auth", "session_token": token})
    return await socket.event("session.ready")


async def post_command(client, session_id, token, operation, fields):
    response = await client.post(
        f"/api/v1/sessions/{session_id}/{operation}",
        json=fields,
        headers={**authorization(token), "Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def start_capture(
    client, session_id, token, socket, *, state_version=0, revision=0
):
    body = await post_command(
        client,
        session_id,
        token,
        "capture",
        {
            "action": "start",
            "expected_revision": revision,
            "expected_state_version": state_version,
        },
    )
    state = await socket.event("session.state")
    assert state.data["reason"] == "start"
    assert state.data["session"]["stream_id"] == body["session"]["stream_id"]
    return body["session"]


def frame_message(stream_id, seq, jpeg_data, *, width=8, height=6):
    return {
        "type": "frame",
        "stream_id": stream_id,
        "frame_seq": seq,
        "capture_ms": seq * 110,
        "width": width,
        "height": height,
        "mirrored": False,
        "image_b64": jpeg_data,
    }


@pytest.mark.asyncio
async def test_real_alphabet_adapter_serves_the_live_api(jpeg_data):
    if (
        not LOCAL_ALPHABET_CHECKPOINT.is_file()
        or not LOCAL_ALPHABET_HAND_MODEL.is_file()
    ):
        pytest.skip("local alphabet assets are required")
    pytest.importorskip("torch")
    pytest.importorskip("torchvision")
    pytest.importorskip("mediapipe")
    app = create_app(
        Settings(
            _env_file=None,
            required_modes=("alphabet",),
            alphabet_checkpoint=LOCAL_ALPHABET_CHECKPOINT,
            alphabet_hand_model=LOCAL_ALPHABET_HAND_MODEL,
        )
    )

    async with (
        app.router.lifespan_context(app),
        client_and_session(app) as (client, sid, token),
    ):
        ready = await client.get("/api/v1/health/ready")
        assert ready.status_code == 200
        assert ready.json()["modes"] == {"alphabet": True, "word": False}
        vocabulary = await client.get("/api/v1/vocabulary?mode=alphabet")
        assert vocabulary.status_code == 200
        labels = vocabulary.json()
        assert len(labels["labels"]) == 31

        async with LiveTestSocket(app, sid) as socket:
            authenticated = await live_auth(socket, token)
            assert (
                authenticated.data["session"]["model_version"]
                == labels["model_version"]
            )
            session = await start_capture(client, sid, token, socket)
            stream_id = session["stream_id"]
            switch = await client.post(
                f"/api/v1/sessions/{sid}/mode",
                headers={**authorization(token), "Idempotency-Key": str(uuid4())},
                json={
                    "mode": "word",
                    "expected_revision": 0,
                    "expected_state_version": session["state_version"],
                },
            )
            assert switch.status_code == 503
            assert switch.json()["error"]["code"] == "MODEL_UNAVAILABLE"
            await socket.send(frame_message(stream_id, 1, jpeg_data))
            ack = await socket.event("frame.ack")
            assert (ack.data["outcome"], ack.data["stream_id"]) == (
                "processed",
                stream_id,
            )
            preview = await socket.event("candidate.updated")
            assert preview.data["candidate"] is None

            ended = await post_command(
                client, sid, token, "end", {"expected_revision": 0}
            )
            assert ended["session"]["status"] == "ended"
            await socket.event("session.ended")
            await socket.expect_close(1000)
        deleted = await client.delete(
            f"/api/v1/sessions/{sid}", headers=authorization(token)
        )
        assert deleted.status_code == 204
    assert app.state.adapter_registry.readiness() == {"alphabet": False, "word": False}


async def make_candidate(socket, stream_id, jpeg_data, now):
    previous_id = None
    for seq in range(1, 5):
        await socket.send(frame_message(stream_id, seq, jpeg_data))
        ack = await socket.event("frame.ack")
        assert ack.data["outcome"] == "processed"
        assert ack.data["frame_seq"] == seq
        assert ack.data["stream_id"] == stream_id
        event = await socket.event("candidate.updated")
        candidate = Candidate.model_validate(event.data["candidate"])
        assert event.event_seq > ack.event_seq
        assert candidate.eligible == (seq == 4)
        if previous_id is not None:
            assert candidate.candidate_id == previous_id
        previous_id = candidate.candidate_id
        now[0] += 0.11
    return candidate


async def confirm(client, session_id, token, socket, candidate, revision):
    body = await post_command(
        client,
        session_id,
        token,
        "confirm",
        {
            "expected_revision": revision,
            "stream_id": candidate.stream_id,
            "candidate_id": candidate.candidate_id,
        },
    )
    assert body["session"]["transcript"]["revision"] == revision + 1
    event = await socket.event("transcript.updated")
    assert event.data["cause"] == "commit"
    assert event.data["committed_item_id"] == body["item_id"]
    assert event.data["session"]["transcript"] == body["session"]["transcript"]
    cleared = await socket.event("candidate.updated")
    assert cleared.data == {"candidate": None}
    return body


@pytest.mark.asyncio
async def test_live_session_switches_both_ways_and_keeps_transcript(
    app_and_time, jpeg_data
):
    app, now = app_and_time
    async with (
        client_and_session(app) as (client, session_id, token),
        LiveTestSocket(app, session_id) as socket,
    ):
        ready = await live_auth(socket, token)
        assert ready.data["confirmation_policy"] == "manual"
        assert ready.data["session"]["status"] == "paused"
        assert ready.event_seq == 0

        capture = await start_capture(client, session_id, token, socket)
        first_stream = capture["stream_id"]
        letter = await make_candidate(socket, first_stream, jpeg_data, now)
        first = await confirm(client, session_id, token, socket, letter, 0)
        assert first["session"]["transcript"]["text"] == "أ"

        await socket.send(frame_message(first_stream, 5, jpeg_data))
        assert (await socket.event("frame.ack")).data["outcome"] == "processed"
        assert (await socket.event("candidate.updated")).data == {"candidate": None}

        switched = await post_command(
            client,
            session_id,
            token,
            "mode",
            {"mode": "word", "expected_revision": 1, "expected_state_version": 1},
        )
        state = await socket.event("session.state")
        word_session = switched["session"]
        assert state.data["reason"] == "mode_changed"
        assert (
            state.data["session"]["stream_id"]
            == word_session["stream_id"]
            != first_stream
        )
        assert word_session["session_id"] == session_id
        assert word_session["status"] == "capturing"
        assert word_session["transcript"] == first["session"]["transcript"]

        await socket.send(frame_message(first_stream, 6, jpeg_data))
        stale = await socket.event("frame.ack")
        assert stale.data["reason"] == "stale_stream"
        word = await make_candidate(socket, word_session["stream_id"], jpeg_data, now)
        second = await confirm(client, session_id, token, socket, word, 1)
        assert second["session"]["transcript"]["text"] == "أ ماء"

        returned = await post_command(
            client,
            session_id,
            token,
            "mode",
            {
                "mode": "alphabet",
                "expected_revision": 2,
                "expected_state_version": 2,
            },
        )
        assert (await socket.event("session.state")).data["reason"] == "mode_changed"
        assert returned["session"]["mode"] == "alphabet"
        assert returned["session"]["transcript"] == second["session"]["transcript"]

        ended = await post_command(
            client, session_id, token, "end", {"expected_revision": 2}
        )
        terminal = await socket.event("session.ended")
        assert terminal.data["session"]["status"] == "ended"
        assert terminal.data["session"]["transcript"] == ended["session"]["transcript"]
        await socket.expect_close(1000)


@pytest.mark.asyncio
async def test_mode_switch_discards_inflight_predictions(app_and_time, jpeg_data):
    app, _ = app_and_time
    alphabet = app.state.adapter_registry.get("alphabet")
    predict = alphabet.predict
    started = threading.Event()
    release = threading.Event()

    def predict_late(frames, times_ms):
        started.set()
        release.wait(1)
        return predict(frames, times_ms)

    alphabet.predict = predict_late
    async with (
        client_and_session(app) as (client, session_id, token),
        LiveTestSocket(app, session_id) as socket,
    ):
        await live_auth(socket, token)
        capture = await start_capture(client, session_id, token, socket)
        await socket.send(frame_message(capture["stream_id"], 1, jpeg_data))
        try:
            assert await asyncio.to_thread(started.wait, 1)
            # Pings are handled while native model inference is blocked.
            await socket.send({"type": "ping", "nonce": "during-inference"})
            assert (await socket.event("pong")).data["nonce"] == "during-inference"
            switched = await post_command(
                client,
                session_id,
                token,
                "mode",
                {
                    "mode": "word",
                    "expected_revision": 0,
                    "expected_state_version": 1,
                },
            )
            assert (await socket.event("session.state")).data[
                "reason"
            ] == "mode_changed"
        finally:
            release.set()
        stale = await socket.event("frame.ack")
        assert stale.data["reason"] == "stale_stream"
        await socket.send(frame_message(switched["session"]["stream_id"], 1, jpeg_data))
        assert (await socket.event("frame.ack")).data["outcome"] == "processed"
        assert (await socket.event("candidate.updated")).data["candidate"][
            "mode"
        ] == "word"
        assert not switched["session"]["transcript"]["items"]


@pytest.mark.asyncio
async def test_capture_pause_and_reconnect_have_fresh_stream(app_and_time, jpeg_data):
    app, _ = app_and_time
    async with client_and_session(app) as (client, session_id, token):
        async with LiveTestSocket(app, session_id) as socket:
            await live_auth(socket, token)
            capture = await start_capture(client, session_id, token, socket)
            paused = await post_command(
                client,
                session_id,
                token,
                "capture",
                {
                    "action": "pause",
                    "expected_revision": 0,
                    "expected_state_version": 1,
                },
            )
            assert (await socket.event("session.state")).data["reason"] == "pause"
            assert paused["session"]["stream_id"] is None
            await socket.send(frame_message(capture["stream_id"], 1, jpeg_data))
            assert (await socket.event("frame.ack")).data["reason"] == "paused"
            active = await start_capture(
                client, session_id, token, socket, state_version=2
            )
            assert active["stream_id"] != capture["stream_id"]
            await socket.send({"type": "ping", "nonce": "before-disconnect"})
            last_event = await socket.event("pong")
        read = await client.get(
            f"/api/v1/sessions/{session_id}", headers=authorization(token)
        )
        assert read.json()["session"]["status"] == "disconnected"
        assert read.json()["session"]["stream_id"] is None

        async with LiveTestSocket(app, session_id) as reconnected:
            ready = await live_auth(reconnected, token)
            assert ready.event_seq > last_event.event_seq
            assert ready.data["session"]["status"] == "paused"
            assert ready.data["session"]["stream_id"] is None
            assert ready.data["session"]["state_version"] == 5
            await reconnected.send(frame_message(active["stream_id"], 1, jpeg_data))
            assert (await reconnected.event("frame.ack")).data["reason"] == "paused"


@pytest.mark.asyncio
async def test_disconnect_cleanup_survives_parent_cancellation(app_and_time):
    app, _ = app_and_time
    async with client_and_session(app) as (client, session_id, token):
        async with LiveTestSocket(app, session_id) as socket:
            await live_auth(socket, token)
            socket.cancel_scope.cancel()
        response = await client.get(
            f"/api/v1/sessions/{session_id}", headers=authorization(token)
        )
        assert response.json()["session"]["status"] == "disconnected"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "origin", [None, "http://localhost:5173.invalid", "http://127.0.0.1:8080"]
)
async def test_origin_requires_exact_allowlist_match(app_and_time, origin):
    app, _ = app_and_time
    async with (
        client_and_session(app) as (_, session_id, _),
        LiveTestSocket(app, session_id, origin=origin) as socket,
    ):
        await socket.expect_close(1008)


@pytest.mark.asyncio
async def test_authentication_timeout_credentials_and_second_socket(app_and_time):
    app, _ = app_and_time
    app.state.live.auth_timeout_seconds = 0.05
    async with client_and_session(app) as (_, session_id, token):
        async with LiveTestSocket(app, session_id) as timed_out:
            await timed_out.expect_accept()
            assert (await timed_out.event("error")).data["error"][
                "code"
            ] == "CREDENTIAL_REQUIRED"
            await timed_out.expect_close(1008)
        async with LiveTestSocket(app, session_id) as wrong:
            await wrong.expect_accept()
            await wrong.send({"type": "auth", "session_token": "wrong-token"})
            assert (await wrong.event("error")).data["error"][
                "code"
            ] == "SESSION_NOT_FOUND"
            await wrong.expect_close(1008)
        async with LiveTestSocket(app, session_id) as owner:
            await live_auth(owner, token)
            async with LiveTestSocket(app, session_id) as duplicate:
                await duplicate.expect_accept()
                await duplicate.send({"type": "auth", "session_token": token})
                error = await duplicate.event("error")
                assert error.data["error"]["code"] == "SOCKET_ALREADY_CONNECTED"
                await duplicate.expect_close(1008)
            await owner.send({"type": "ping", "nonce": "still-connected"})
            assert (await owner.event("pong")).data == {"nonce": "still-connected"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("message", "close_code", "error_code"),
    [
        ({"bytes": b"\x00\xff"}, 1007, "VALIDATION_ERROR"),
        (
            {"text": '{"type":"ping","type":"ping","protocol_version":1}'},
            1007,
            "VALIDATION_ERROR",
        ),
        (
            {"text": '{"type":"ping","protocol_version":true,"nonce":"x"}'},
            1007,
            "VALIDATION_ERROR",
        ),
        ({"text": "x" * 262_145}, 1009, "PAYLOAD_TOO_LARGE"),
    ],
)
async def test_malformed_or_oversize_live_input(
    app_and_time, message, close_code, error_code
):
    app, _ = app_and_time
    async with (
        client_and_session(app) as (_, session_id, token),
        LiveTestSocket(app, session_id) as socket,
    ):
        await live_auth(socket, token)
        await socket.send_raw(**message)
        assert (await socket.event("error")).data["error"]["code"] == error_code
        await socket.expect_close(close_code)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid", ["base64", "jpeg", "dimensions", "declared_limit", "non_finite"]
)
async def test_invalid_camera_frame_is_rejected_before_model(
    app_and_time, jpeg_data, invalid
):
    app, _ = app_and_time
    async with (
        client_and_session(app) as (client, session_id, token),
        LiveTestSocket(app, session_id) as socket,
    ):
        await live_auth(socket, token)
        capture = await start_capture(client, session_id, token, socket)
        frame = frame_message(capture["stream_id"], 1, jpeg_data)
        violations = {
            "base64": {"image_b64": "data:image/jpeg;base64," + jpeg_data},
            "jpeg": {"image_b64": base64.b64encode(b"not a JPEG").decode()},
            "dimensions": {"width": 9},
            "declared_limit": {"width": 641},
            "non_finite": {"capture_ms": float("inf")},
        }
        await socket.send({**frame, **violations[invalid]})
        error = await socket.event("error")
        assert error.data["error"]["code"] == (
            "PAYLOAD_TOO_LARGE" if invalid == "declared_limit" else "VALIDATION_ERROR"
        )
        await socket.expect_close(1009 if invalid == "declared_limit" else 1007)
    assert app.state.adapter_registry.get("alphabet").samples == []


@pytest.mark.asyncio
@pytest.mark.parametrize("termination", ["delete", "expiry"])
async def test_delete_and_idle_expiry_send_content_free_terminal_events(
    app_and_time, termination
):
    app, now = app_and_time
    async with (
        client_and_session(app) as (client, session_id, token),
        LiveTestSocket(app, session_id) as socket,
    ):
        await live_auth(socket, token)
        await socket.send({"type": "ping", "nonce": "ping-before-terminal"})
        assert (await socket.event("pong")).data["nonce"] == "ping-before-terminal"
        if termination == "delete":
            response = await client.delete(
                f"/api/v1/sessions/{session_id}", headers=authorization(token)
            )
            assert response.status_code == 204
            terminal = await socket.event("session.deleted")
            assert terminal.data == {"reason": "user"}
        else:
            now[0] += app.state.settings.idle_timeout_seconds
            await socket.send({"type": "ping", "nonce": "after-idle-expiry"})
            terminal = await socket.event("session.expired")
            assert terminal.data == {"reason": "idle"}
        await socket.expect_close(1000)


@pytest.mark.asyncio
async def test_live_connection_caps_pending_auth_and_idle_link(app_and_time):
    app, _ = app_and_time
    app.state.live.max_pending_auth = 1
    app.state.live.link_timeout_seconds = 0.05
    async with (
        client_and_session(app) as (_, session_id, token),
        LiveTestSocket(app, session_id) as first,
    ):
        await first.expect_accept()
        async with LiveTestSocket(app, session_id) as refused:
            await refused.expect_close(1013)
        await first.send({"type": "auth", "session_token": token})
        ready = await first.event("session.ready")
        assert ready.data["session"]["status"] == "paused"
        await first.expect_close(1013)


@pytest.mark.asyncio
async def test_temporal_warmup_warns_when_frame_rate_is_too_low(
    app_and_time, jpeg_data
):
    app, now = app_and_time
    adapter = app.state.adapter_registry.get("word")
    adapter.window_samples = 3
    adapter.required_sample_fps = 5

    async with (
        client_and_session(app, "word") as (client, session_id, token),
        LiveTestSocket(app, session_id) as socket,
    ):
        await live_auth(socket, token)
        capture = await start_capture(client, session_id, token, socket)
        for seq in range(1, 4):
            frame = frame_message(capture["stream_id"], seq, jpeg_data)
            await socket.send({**frame, "capture_ms": seq * 250})
            ack = await socket.event("frame.ack")
            if seq < 3:
                assert ack.data["outcome"] == "processed"
            else:
                assert ack.data["reason"] == "gap_reset"
                warning = await socket.event("warning")
                assert warning.data["code"] == "insufficient_rate"
                assert warning.data["frame_seq"] == 3
            assert (await socket.event("candidate.updated")).data == {"candidate": None}
            now[0] += 0.25

    assert adapter.samples == []


@pytest.mark.asyncio
async def test_adapter_failure_sends_safe_terminal_error(app_and_time, jpeg_data):
    app, _ = app_and_time
    adapter = app.state.adapter_registry.get("alphabet")

    def fail(*_args):
        raise RuntimeError("private model path")

    adapter.predict = fail
    async with (
        client_and_session(app) as (client, session_id, token),
        LiveTestSocket(app, session_id) as socket,
    ):
        await live_auth(socket, token)
        capture = await start_capture(client, session_id, token, socket)
        await socket.send(frame_message(capture["stream_id"], 1, jpeg_data))
        error = await socket.event("error")
        assert error.data["error"]["code"] == "INTERNAL_ERROR"
        assert error.data["related_frame_seq"] == 1
        assert "private model path" not in error.model_dump_json()
        await socket.expect_close(1011)
