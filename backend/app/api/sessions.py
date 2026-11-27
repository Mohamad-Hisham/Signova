"""Session lifecycle and recognition commands."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Header, Request, Response

from app.api.session_access import (
    Authorization,
    check_session_current,
    execute_session_command,
    rate_limited,
    require_command_id,
    require_session,
    session_access_error,
)
from app.schemas.common import ErrorEnvelope
from app.schemas.rest import (
    CaptureRequest,
    ConfirmRequest,
    ConfirmResponse,
    EndRequest,
    ModeChangeRequest,
    SessionCreatedResponse,
    SessionCreateRequest,
    SessionResponse,
)
from app.services.commands import check_revision, check_state_version
from app.services.recognition import StaleStreamError
from app.services.sessions import (
    SessionDeleted,
    SessionExpired,
    SessionLimitExceeded,
    SessionNotFound,
    SessionRecord,
    SessionStore,
)
from app.services.transcript import (
    TranscriptLimitExceeded,
    append_model_item,
    derive_text,
    public_transcript_items,
)
from app.utilities.errors import ApiError
from app.utilities.time import utc_now

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])
CommandKey = Annotated[str | None, Header(alias="Idempotency-Key")]
VALIDATION_RESPONSE = {
    413: {"model": ErrorEnvelope, "description": "Request body too large"},
    422: {"model": ErrorEnvelope, "description": "Invalid request"},
}
ACCESS_RESPONSES = {
    401: {"model": ErrorEnvelope, "description": "Session capability required"},
    404: {"model": ErrorEnvelope, "description": "Session unavailable"},
    410: {"model": ErrorEnvelope, "description": "Session deleted or expired"},
}
MUTATION_RESPONSES = {
    **ACCESS_RESPONSES,
    **VALIDATION_RESPONSE,
    409: {"model": ErrorEnvelope, "description": "Session or command conflict"},
    429: {"model": ErrorEnvelope, "description": "Request limit reached"},
}
MODEL_RESPONSE = {
    503: {"model": ErrorEnvelope, "description": "Selected model unavailable"}
}


def snapshot(record: SessionRecord, store: SessionStore) -> dict:
    deadline, _ = store.deadline(record)
    monotonic_now = store.clock.now_monotonic()
    now = utc_now()
    expires_at = now + timedelta(seconds=max(0.0, deadline - monotonic_now))
    absolute_expires_at = now + timedelta(
        seconds=max(0.0, record.absolute_deadline - monotonic_now)
    )
    return {
        "session_id": record.session_id,
        "mode": record.mode,
        "status": record.status,
        "state_version": record.state_version,
        "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
        "absolute_expires_at": absolute_expires_at.isoformat().replace("+00:00", "Z"),
        "idle_timeout_seconds": store.idle_timeout_seconds,
        "reconnect_grace_seconds": store.reconnect_grace_seconds,
        "model_version": record.model_version,
        "stream_id": record.stream_id,
        "recovery_enabled": record.recovery_enabled,
        "transcript": {
            "revision": record.transcript_revision,
            "items": public_transcript_items(record.items),
            "text": derive_text(record.mode, record.items),
            "updated_at": record.updated_at.isoformat().replace("+00:00", "Z"),
        },
    }


def _adapter(request: Request, mode: str):
    try:
        return request.app.state.adapter_registry.get(mode)
    except KeyError as exc:
        raise ApiError(
            503,
            "MODEL_UNAVAILABLE",
            "This recognition mode is unavailable.",
            retryable=True,
        ) from exc


def _state_response(request: Request, record: SessionRecord, reason: str) -> dict:
    state = request.app.state
    result = {"session": snapshot(record, state.session_store)}
    state.live.publish(
        record,
        "session.state",
        {**result, "reason": reason},
        discard_pending=reason in {"pause", "mode_changed", "limit"},
    )
    return result


def _pause(request: Request, record: SessionRecord) -> None:
    if record.stream_id is not None:
        request.app.state.recognition_service.invalidate_stream(record.stream_id)
    record.stream_id = None
    record.status = "paused"
    record.state_version += 1


@router.post(
    "",
    status_code=201,
    response_model=SessionCreatedResponse,
    responses={
        **VALIDATION_RESPONSE,
        **MODEL_RESPONSE,
        429: {"model": ErrorEnvelope, "description": "Capacity or rate limit reached"},
    },
)
async def create_session(request: Request, body: SessionCreateRequest):
    """Create a paused session for a ready recognition mode."""
    state = request.app.state
    source = request.client.host if request.client else "unknown"
    retry_after = state.creation_rate.take(source)
    if retry_after is not None:
        raise rate_limited(retry_after)

    adapter = _adapter(request, body.mode)
    try:
        record, token = state.session_store.create(
            body.mode,
            model_version=adapter.model_version,
            recovery_enabled=body.recovery_enabled,
        )
    except SessionLimitExceeded as exc:
        raise ApiError(
            429,
            "SESSION_LIMIT",
            "The server has reached its session capacity.",
            retryable=True,
            headers={"Retry-After": str(state.settings.sweep_interval_seconds)},
        ) from exc

    return {"session": snapshot(record, state.session_store), "session_token": token}


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    responses={**ACCESS_RESPONSES, **VALIDATION_RESPONSE},
)
async def read_session(
    request: Request, session_id: str, authorization: Authorization = None
):
    record = require_session(request, session_id, authorization)
    async with record.lock:
        check_session_current(request, record)
        return {"session": snapshot(record, request.app.state.session_store)}


@router.post(
    "/{session_id}/capture",
    response_model=SessionResponse,
    responses={**MUTATION_RESPONSES, **MODEL_RESPONSE},
)
async def capture_session(
    request: Request,
    session_id: str,
    body: CaptureRequest,
    authorization: Authorization = None,
    idempotency_key: CommandKey = None,
):
    record = require_session(request, session_id, authorization)
    command_id = require_command_id(idempotency_key)
    state = request.app.state

    def operation() -> dict:
        check_revision(record, body.expected_revision)
        check_state_version(record, body.expected_state_version)
        if body.action == "start":
            if record.socket_id is None:
                raise ApiError(
                    409, "SOCKET_REQUIRED", "Connect the live socket before starting."
                )
            if record.status == "capturing":
                raise ApiError(409, "ALREADY_CAPTURING", "Capture is already active.")
            _adapter(request, record.mode)
            record.stream_id = state.recognition_service.start_stream(
                record.mode
            ).stream_id
            record.status = "capturing"
            record.state_version += 1
        else:
            if record.status != "capturing":
                return {"session": snapshot(record, state.session_store)}
            _pause(request, record)

        state.session_store.touch_idle(record)
        return _state_response(request, record, body.action)

    async with record.lock:
        return execute_session_command(request, record, command_id, body, operation)


@router.post(
    "/{session_id}/mode",
    response_model=SessionResponse,
    responses={**MUTATION_RESPONSES, **MODEL_RESPONSE},
)
async def change_session_mode(
    request: Request,
    session_id: str,
    body: ModeChangeRequest,
    authorization: Authorization = None,
    idempotency_key: CommandKey = None,
):
    """Change the active recognition mode while retaining the session and transcript."""
    record = require_session(request, session_id, authorization)
    command_id = require_command_id(idempotency_key)
    state = request.app.state

    def operation() -> dict:
        check_revision(record, body.expected_revision)
        check_state_version(record, body.expected_state_version)
        if record.mode == body.mode:
            return {"session": snapshot(record, state.session_store)}

        adapter = _adapter(request, body.mode)
        recognition = state.recognition_service
        new_stream_id = None
        if record.status == "capturing":
            new_stream_id = recognition.start_stream(body.mode).stream_id
        if record.stream_id is not None:
            recognition.invalidate_stream(record.stream_id)

        record.mode = body.mode
        record.model_version = adapter.model_version
        record.stream_id = new_stream_id
        record.state_version += 1
        state.session_store.touch_idle(record)
        return _state_response(request, record, "mode_changed")

    async with record.lock:
        return execute_session_command(request, record, command_id, body, operation)


@router.post(
    "/{session_id}/confirm",
    response_model=ConfirmResponse,
    responses=MUTATION_RESPONSES,
)
async def confirm_session(
    request: Request,
    session_id: str,
    body: ConfirmRequest,
    authorization: Authorization = None,
    idempotency_key: CommandKey = None,
):
    record = require_session(request, session_id, authorization)
    command_id = require_command_id(idempotency_key)
    state = request.app.state

    def operation() -> dict:
        check_revision(record, body.expected_revision)
        if record.stream_id != body.stream_id:
            raise ApiError(409, "STALE_STREAM", "The capture stream has changed.")
        if record.status != "capturing":
            raise ApiError(
                409, "CANDIDATE_UNAVAILABLE", "The candidate is unavailable."
            )

        def append(prediction):
            return append_model_item(
                record,
                text=prediction.text,
                kind="word" if record.mode == "word" else "letter",
                label_id=prediction.label_id,
                score=prediction.score,
                model_version=prediction.model_version,
                confirmed_by="manual",
            )

        try:
            item = state.recognition_service.commit_candidate(
                body.stream_id, body.candidate_id, append
            )
        except StaleStreamError as exc:
            raise ApiError(
                409, "CANDIDATE_UNAVAILABLE", "The candidate is unavailable."
            ) from exc
        except TranscriptLimitExceeded as exc:
            _pause(request, record)
            _state_response(request, record, "limit")
            raise ApiError(
                409, "TRANSCRIPT_LIMIT", "The transcript limit would be exceeded."
            ) from exc

        state.session_store.touch_idle(record)
        session = snapshot(record, state.session_store)
        state.live.publish(
            record,
            "transcript.updated",
            {
                "session": session,
                "cause": "commit",
                "command_id": command_id,
                "committed_item_id": item["item_id"],
            },
        )
        state.live.publish(record, "candidate.updated", {"candidate": None})
        return {"session": session, "item_id": item["item_id"]}

    async with record.lock:
        return execute_session_command(request, record, command_id, body, operation)


@router.post(
    "/{session_id}/end", response_model=SessionResponse, responses=MUTATION_RESPONSES
)
async def end_session(
    request: Request,
    session_id: str,
    body: EndRequest,
    authorization: Authorization = None,
    idempotency_key: CommandKey = None,
):
    record = require_session(request, session_id, authorization)
    command_id = require_command_id(idempotency_key)
    state = request.app.state

    def operation() -> dict:
        check_revision(record, body.expected_revision)
        if record.stream_id is not None:
            state.recognition_service.invalidate_stream(record.stream_id)
        state.session_store.mark_ended(record)
        result = {"session": snapshot(record, state.session_store)}
        state.live.publish(
            record,
            "session.ended",
            {**result, "reason": "user"},
            discard_pending=True,
            close_code=1000,
        )
        return result

    async with record.lock:
        return execute_session_command(
            request, record, command_id, body, operation, allow_ended_replay=True
        )


@router.delete(
    "/{session_id}",
    status_code=204,
    responses={**ACCESS_RESPONSES, **VALIDATION_RESPONSE},
)
async def delete_session(
    request: Request, session_id: str, authorization: Authorization = None
):
    try:
        record = require_session(request, session_id, authorization)
        async with record.lock:
            try:
                request.app.state.session_store.delete(record)
            except (SessionDeleted, SessionExpired, SessionNotFound) as exc:
                raise session_access_error(exc) from exc
    except ApiError as exc:
        if exc.envelope.error.code != "SESSION_DELETED":
            raise
    return Response(status_code=204)
