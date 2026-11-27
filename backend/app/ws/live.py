"""Authenticate and serve the Signova live session protocol."""

import asyncio
import base64
import binascii
import json
import math
from dataclasses import dataclass, field
from io import BytesIO

from anyio import CancelScope
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from PIL import Image
from pydantic import ValidationError

from app.api.sessions import snapshot
from app.config import Settings
from app.schemas.events import AuthMessage, FrameMessage, PingMessage, ServerEnvelope
from app.services.recognition import (
    FrameGapError,
    InferenceTimeoutError,
    InsufficientRateError,
    OverloadedError,
    RateLimitError,
    StaleFrameError,
    StaleStreamError,
)
from app.services.sessions import (
    SessionDeleted,
    SessionExpired,
    SessionNotFound,
    SessionRecord,
)
from app.utilities.errors import build_error
from app.utilities.ids import new_uuid, validate_uuid
from app.utilities.time import utc_now

router = APIRouter()
_SESSION_GONE = (SessionDeleted, SessionExpired, SessionNotFound)
_DISCARD_REASONS = {
    FrameGapError: "gap_reset",
    InsufficientRateError: "gap_reset",
    OverloadedError: "overload",
    RateLimitError: "rate_limit",
    StaleFrameError: "stale_frame",
    StaleStreamError: "stale_stream",
}


class ProtocolError(Exception):
    def __init__(self, close_code: int, error_code: str, message: str):
        self.close_code = close_code
        self.error_code = error_code
        self.message = message


def _invalid_message(message: str = "Invalid live message.") -> ProtocolError:
    return ProtocolError(1007, "VALIDATION_ERROR", message)


def _too_large() -> ProtocolError:
    return ProtocolError(
        1009, "PAYLOAD_TOO_LARGE", "Live message or image exceeds its limit."
    )


def _policy_error(code: str, message: str) -> ProtocolError:
    return ProtocolError(1008, code, message)


def _envelope(session_id: str, seq: int, event_type: str, data: dict) -> dict:
    return ServerEnvelope(
        protocol_version=1,
        type=event_type,
        event_id=new_uuid(),
        event_seq=seq,
        session_id=session_id,
        at=utc_now(),
        data=data,
    ).model_dump(mode="json")


def _error_data(
    error_code: str,
    message: str,
    *,
    retryable: bool = False,
    frame_seq: int | None = None,
) -> dict:
    return {
        **build_error(error_code, message, retryable=retryable).model_dump(),
        "related_frame_seq": frame_seq,
        "command_id": None,
    }


@dataclass(frozen=True)
class Outbound:
    event: dict | None = None
    close_code: int | None = None


@dataclass
class LiveConnection:
    queue: asyncio.Queue[Outbound]
    socket_id: str = field(default_factory=new_uuid)
    finished: asyncio.Event = field(default_factory=asyncio.Event)
    closing: bool = False
    frame_task: asyncio.Task | None = None

    def push(self, outbound: Outbound, *, discard_pending: bool = False) -> None:
        if self.closing:
            return
        if self.queue.full() and not discard_pending:
            outbound = Outbound(close_code=1013)
            discard_pending = True
        if discard_pending:
            while not self.queue.empty():
                self.queue.get_nowait()
        if outbound.close_code is not None:
            self.closing = True
        self.queue.put_nowait(outbound)


class WebSocketHub:
    def __init__(
        self,
        *,
        max_pending_auth: int = 20,
        max_outbound: int = 24,
        auth_timeout_seconds: float = 5.0,
        link_timeout_seconds: float = 45.0,
        write_timeout_seconds: float = 5.0,
    ):
        self.max_pending_auth = max_pending_auth
        self.max_outbound = max_outbound
        self.auth_timeout_seconds = auth_timeout_seconds
        self.link_timeout_seconds = link_timeout_seconds
        self.write_timeout_seconds = write_timeout_seconds
        self._pending_auth = 0
        self._connections: dict[str, LiveConnection] = {}

    def enter_auth(self) -> bool:
        if self._pending_auth >= self.max_pending_auth:
            return False
        self._pending_auth += 1
        return True

    def leave_auth(self) -> None:
        self._pending_auth -= 1

    def register(self, record: SessionRecord) -> LiveConnection:
        connection = LiveConnection(asyncio.Queue(maxsize=self.max_outbound))
        self._connections[record.session_id] = connection
        record.socket_id = connection.socket_id
        return connection

    def remove(self, session_id: str, connection: LiveConnection) -> None:
        if self._connections.get(session_id) is connection:
            del self._connections[session_id]

    def publish(
        self,
        record: SessionRecord,
        event_type: str,
        data: dict,
        *,
        discard_pending: bool = False,
        close_code: int | None = None,
    ) -> None:
        connection = self._connections.get(record.session_id)
        if connection is None or connection.closing:
            return
        event = _envelope(record.session_id, record.event_seq, event_type, data)
        record.event_seq += 1
        connection.push(Outbound(event, close_code), discard_pending=discard_pending)

    def close_all(self) -> None:
        for connection in self._connections.values():
            connection.push(Outbound(close_code=1012), discard_pending=True)


def _unique_json_fields(fields: list[tuple[str, object]]) -> dict:
    values = {}
    for key, value in fields:
        if key in values:
            raise ValueError("Duplicate JSON field")
        values[key] = value
    return values


def _invalid_json_constant(value: str) -> None:
    raise ValueError("Non-finite JSON number")


async def _receive_json(websocket: WebSocket, max_message_bytes: int) -> dict:
    message = await websocket.receive()
    if message["type"] == "websocket.disconnect":
        raise WebSocketDisconnect(message["code"])
    payload = message.get("text")
    if payload is None:
        raise _invalid_message("Live messages must contain text JSON.")
    if len(payload) > max_message_bytes:
        raise _too_large()
    try:
        if len(payload.encode("utf-8")) > max_message_bytes:
            raise _too_large()
        data = json.loads(
            payload,
            object_pairs_hook=_unique_json_fields,
            parse_constant=_invalid_json_constant,
        )
    except (ValueError, RecursionError):
        raise _invalid_message() from None
    if not isinstance(data, dict):
        raise _invalid_message()
    if type(data.get("protocol_version")) is not int or data["protocol_version"] != 1:
        raise _invalid_message("Unsupported live protocol version.")
    return data


def _parse_frame(data: dict, settings: Settings) -> FrameMessage:
    for field_name, limit in (
        ("width", settings.max_jpeg_width),
        ("height", settings.max_jpeg_height),
    ):
        value = data.get(field_name)
        if type(value) is int and value > limit:
            raise _too_large()
    encoded = data.get("image_b64")
    if isinstance(encoded, str) and len(encoded) > 4 * (
        (settings.max_jpeg_bytes + 2) // 3
    ):
        raise _too_large()
    if data.get("mirrored") is not False:
        raise _invalid_message("Camera frames must be unmirrored.")
    frame = FrameMessage.model_validate(data, strict=True)
    if not math.isfinite(frame.capture_ms):
        raise _invalid_message("Capture time must be finite.")
    return frame


def _load_jpeg(frame: FrameMessage, settings: Settings) -> bytes:
    try:
        jpeg = base64.b64decode(frame.image_b64, validate=True)
        canonical = base64.b64encode(jpeg).decode("ascii")
    except (binascii.Error, ValueError):
        raise _invalid_message(
            "Camera frame must contain strict base64 JPEG."
        ) from None
    if len(jpeg) > settings.max_jpeg_bytes:
        raise _too_large()
    if canonical != frame.image_b64 or not jpeg.startswith(b"\xff\xd8\xff"):
        raise _invalid_message("Camera frame must contain strict base64 JPEG.")
    try:
        with Image.open(BytesIO(jpeg), formats=("JPEG",)) as image:
            if image.size != (frame.width, frame.height):
                raise _invalid_message(
                    "Camera frame dimensions do not match its metadata."
                )
            image.load()
    except Image.DecompressionBombError:
        raise _too_large() from None
    except (OSError, ValueError, SyntaxError):
        raise _invalid_message("Camera frame is not a valid JPEG.") from None
    return jpeg


async def _send(
    websocket: WebSocket, connection: LiveConnection, hub: WebSocketHub
) -> None:
    try:
        while True:
            outbound = await connection.queue.get()
            if outbound.event is not None:
                await asyncio.wait_for(
                    websocket.send_json(outbound.event),
                    timeout=hub.write_timeout_seconds,
                )
            if outbound.close_code is not None:
                await _close(websocket, outbound.close_code, hub.write_timeout_seconds)
                return
    except TimeoutError:
        await _close(websocket, 1013, hub.write_timeout_seconds)
    except (RuntimeError, WebSocketDisconnect, OSError):
        pass
    finally:
        connection.finished.set()


async def _close(websocket: WebSocket, code: int, timeout: float) -> None:
    try:
        await asyncio.wait_for(websocket.close(code), timeout=timeout)
    except (RuntimeError, WebSocketDisconnect, OSError, TimeoutError):
        pass


async def _reject(
    websocket: WebSocket, session_id: str, error: ProtocolError, hub: WebSocketHub
) -> None:
    try:
        await asyncio.wait_for(
            websocket.send_json(
                _envelope(
                    session_id, 0, "error", _error_data(error.error_code, error.message)
                )
            ),
            timeout=hub.write_timeout_seconds,
        )
    except (RuntimeError, WebSocketDisconnect, OSError, TimeoutError):
        pass
    await _close(websocket, error.close_code, hub.write_timeout_seconds)


async def _authenticate(
    websocket: WebSocket, session_id: str, hub: WebSocketHub, settings: Settings
) -> tuple[SessionRecord, LiveConnection]:
    store = websocket.app.state.session_store
    try:
        data = await asyncio.wait_for(
            _receive_json(websocket, settings.max_message_bytes),
            timeout=hub.auth_timeout_seconds,
        )
    except TimeoutError:
        raise _policy_error(
            "CREDENTIAL_REQUIRED", "Live authentication timed out."
        ) from None
    if data.get("type") != "auth":
        raise _policy_error(
            "CREDENTIAL_REQUIRED", "The first live message must authenticate."
        )
    try:
        auth = AuthMessage.model_validate(data, strict=True)
    except ValidationError:
        raise _policy_error(
            "CREDENTIAL_REQUIRED", "Invalid live authentication."
        ) from None

    try:
        record = store.authenticate(session_id, auth.session_token)
        async with record.lock:
            store.check_current(record)
            if record.status == "ended":
                raise _policy_error("SESSION_ENDED", "This session has ended.")
            if record.socket_id is not None:
                raise _policy_error(
                    "SOCKET_ALREADY_CONNECTED",
                    "This session already has a live connection.",
                )
            if record.status == "disconnected":
                record.status = "paused"
                record.reconnect_deadline = None
                record.state_version += 1
            ready = snapshot(record, store)
            connection = hub.register(record)
            hub.publish(
                record,
                "session.ready",
                {"session": ready, "confirmation_policy": "manual"},
            )
    except SessionExpired:
        raise _policy_error("SESSION_EXPIRED", "This session has expired.") from None
    except SessionDeleted:
        raise _policy_error(
            "SESSION_DELETED", "This session has been deleted."
        ) from None
    except SessionNotFound:
        raise _policy_error(
            "SESSION_NOT_FOUND", "The requested session was not found."
        ) from None
    return record, connection


def _ack(
    hub: WebSocketHub,
    record: SessionRecord,
    frame: FrameMessage,
    arrival: float,
    now: float,
    discard_reason: str | None = None,
) -> None:
    hub.publish(
        record,
        "frame.ack",
        {
            "stream_id": frame.stream_id,
            "frame_seq": frame.frame_seq,
            "outcome": "discarded" if discard_reason else "processed",
            "reason": discard_reason,
            "processing_ms": max(0.0, (now - arrival) * 1000),
        },
    )


def _frame_error(
    hub: WebSocketHub,
    record: SessionRecord,
    error: ProtocolError,
    frame_seq: int | None = None,
) -> None:
    hub.publish(
        record,
        "error",
        _error_data(error.error_code, error.message, frame_seq=frame_seq),
        discard_pending=True,
        close_code=error.close_code,
    )


async def _process_frame(
    websocket: WebSocket, record: SessionRecord, frame: FrameMessage, arrival: float
) -> None:
    store = websocket.app.state.session_store
    hub = websocket.app.state.live
    recognition = websocket.app.state.recognition_service

    def renew_idle() -> None:
        store.check_current(record)
        store.touch_idle(record)

    error = None
    try:
        await recognition.process_admitted_frame(
            frame.stream_id, on_admitted=renew_idle
        )
    except _SESSION_GONE:
        return
    except Exception as exc:  # noqa: BLE001 - map native model failures to a safe close
        error = exc

    async with record.lock:
        try:
            store.check_current(record)
        except _SESSION_GONE:
            return

        now = store.clock.now_monotonic()
        if record.status != "capturing" or frame.stream_id != record.stream_id:
            _ack(hub, record, frame, arrival, now, "stale_stream")
            return

        if isinstance(error, ProtocolError):
            _frame_error(hub, record, error, frame.frame_seq)
            return
        if isinstance(error, InferenceTimeoutError):
            _ack(hub, record, frame, arrival, now, "overload")
            hub.publish(
                record,
                "error",
                _error_data(
                    "INFERENCE_TIMEOUT",
                    "Recognition timed out.",
                    retryable=True,
                    frame_seq=frame.frame_seq,
                ),
            )
        elif error is not None:
            reason = _DISCARD_REASONS.get(type(error))
            if reason is None:
                _frame_error(
                    hub,
                    record,
                    ProtocolError(1011, "INTERNAL_ERROR", "Live recognition failed."),
                    frame.frame_seq,
                )
                return
            _ack(hub, record, frame, arrival, now, reason)
            if isinstance(error, InsufficientRateError):
                hub.publish(
                    record,
                    "warning",
                    {
                        "code": "insufficient_rate",
                        "message": "Camera samples did not meet the model's required rate.",
                        "frame_seq": frame.frame_seq,
                    },
                )
        else:
            _ack(hub, record, frame, arrival, now)
        hub.publish(
            record,
            "candidate.updated",
            {"candidate": recognition.candidate_view(frame.stream_id)},
        )


def _admit_frame(
    websocket: WebSocket,
    record: SessionRecord,
    connection: LiveConnection,
    frame: FrameMessage,
    settings: Settings,
) -> None:
    hub = websocket.app.state.live
    recognition = websocket.app.state.recognition_service
    now = websocket.app.state.session_store.clock.now_monotonic()
    if record.status != "capturing":
        _ack(hub, record, frame, now, now, "paused")
        return
    if frame.stream_id != record.stream_id:
        _ack(hub, record, frame, now, now, "stale_stream")
        return
    try:
        recognition.admit_frame(
            frame.stream_id,
            frame.frame_seq,
            frame.capture_ms,
            lambda: _load_jpeg(frame, settings),
            max_fps=settings.max_fps,
        )
        if connection.frame_task is not None and not connection.frame_task.done():
            recognition.break_continuity(frame.stream_id)
            raise OverloadedError
    except (
        FrameGapError,
        OverloadedError,
        RateLimitError,
        StaleFrameError,
        StaleStreamError,
    ) as error:
        _ack(hub, record, frame, now, now, _DISCARD_REASONS[type(error)])
        hub.publish(record, "candidate.updated", {"candidate": None})
        return
    connection.frame_task = asyncio.create_task(
        _process_frame(websocket, record, frame, now)
    )


async def _read(
    websocket: WebSocket,
    record: SessionRecord,
    connection: LiveConnection,
    settings: Settings,
) -> None:
    hub = websocket.app.state.live
    store = websocket.app.state.session_store
    try:
        while not connection.closing:
            data = await asyncio.wait_for(
                _receive_json(websocket, settings.max_message_bytes),
                timeout=hub.link_timeout_seconds,
            )
            message_type = data.get("type")
            if message_type == "frame":
                frame = _parse_frame(data, settings)
            elif message_type == "ping":
                ping = PingMessage.model_validate(data, strict=True)
            else:
                raise _invalid_message(
                    "Only camera frames and pings follow live authentication."
                )

            async with record.lock:
                store.check_current(record)
                if connection.closing:
                    break
                if message_type == "frame":
                    _admit_frame(websocket, record, connection, frame, settings)
                else:
                    hub.publish(record, "pong", {"nonce": ping.nonce})
    except WebSocketDisconnect:
        return
    except TimeoutError:
        connection.push(Outbound(close_code=1013), discard_pending=True)
    except _SESSION_GONE:
        connection.push(Outbound(close_code=1000), discard_pending=True)
    except ValidationError:
        _frame_error(hub, record, _invalid_message())
    except ProtocolError as error:
        _frame_error(hub, record, error)
    except Exception:  # noqa: BLE001 - contain unexpected failures at the socket boundary
        _frame_error(
            hub, record, ProtocolError(1011, "INTERNAL_ERROR", "Live session failed.")
        )
    await connection.finished.wait()


async def _detach(
    websocket: WebSocket,
    record: SessionRecord,
    connection: LiveConnection,
    hub: WebSocketHub,
) -> None:
    store = websocket.app.state.session_store
    async with record.lock:
        hub.remove(record.session_id, connection)
        if record.socket_id != connection.socket_id:
            return
        record.socket_id = None
        try:
            store.check_current(record)
        except _SESSION_GONE:
            return
        if record.status == "ended":
            return
        if record.stream_id is not None:
            websocket.app.state.recognition_service.invalidate_stream(record.stream_id)
        record.stream_id = None
        record.status = "disconnected"
        record.state_version += 1
        record.reconnect_deadline = store.clock.deadline(store.reconnect_grace_seconds)


@router.websocket("/api/v1/ws/sessions/{session_id}")
async def live_session(websocket: WebSocket, session_id: str) -> None:
    hub = websocket.app.state.live
    settings = websocket.app.state.settings
    origins = websocket.headers.getlist("origin")
    if (
        len(origins) != 1
        or origins[0] not in settings.cors_origins
        or websocket.url.query
    ):
        await _close(websocket, 1008, hub.write_timeout_seconds)
        return
    try:
        validate_uuid(session_id)
    except ValueError:
        await _close(websocket, 1008, hub.write_timeout_seconds)
        return
    if not hub.enter_auth():
        await _close(websocket, 1013, hub.write_timeout_seconds)
        return

    try:
        await websocket.accept()
        record, connection = await _authenticate(websocket, session_id, hub, settings)
    except WebSocketDisconnect:
        return
    except ProtocolError as error:
        await _reject(websocket, session_id, error, hub)
        return
    except Exception:  # noqa: BLE001 - contain unexpected failures at the socket boundary
        await _reject(
            websocket,
            session_id,
            ProtocolError(1011, "INTERNAL_ERROR", "Live session failed."),
            hub,
        )
        return
    finally:
        hub.leave_auth()

    tasks = (
        asyncio.create_task(_send(websocket, connection, hub)),
        asyncio.create_task(_read(websocket, record, connection, settings)),
    )
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        with CancelScope(shield=True):
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            if connection.frame_task is not None:
                connection.frame_task.cancel()
                await asyncio.gather(connection.frame_task, return_exceptions=True)
            await _detach(websocket, record, connection, hub)
