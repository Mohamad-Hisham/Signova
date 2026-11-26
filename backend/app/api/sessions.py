# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve REST create/read/capture/confirm/space/end/delete session boundaries.
# Owner: Ali.
# Expected inputs: Validated body/headers, per-session bearer capability and service results.
# Expected outputs: Future exact statuses, one-time token and canonical session
#   snapshots/item_id.
# Responsibilities: Delegate authority, locking, deadline and command identity to services;
#   preserve no-body delete semantics.
# Connections: schemas, services/sessions.py, commands.py, recognition.py and transcript.py.
# Future implementation: Implement the documented existing routes without new account/auth
#   infrastructure.
# Rules and limitations: No model inference/training in routes, alternate mode aliases, public
#   listing or token in read responses.
# Expected tests or acceptance: All session routes enforce access/expiry/state/revision;
#   deletion replay/tombstone edges await documented resolution.

from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse

from app.schemas.rest import (
    CaptureRequest,
    ConfirmRequest,
    SessionCreateRequest,
)
from app.services.commands import (
    IdempotencyConflict,
    RevisionConflict,
    StateConflict,
    check_revision,
    check_state_version,
)
from app.services.recognition import StaleStreamError
from app.services.sessions import (
    SessionExpired,
    SessionLimitExceeded,
    SessionNotFound,
)
from app.services.transcript import (
    TranscriptLimitExceeded,
    append_model_item,
    derive_text,
)
from app.utilities.errors import build_error
from app.utilities.ids import validate_uuid
from app.utilities.time import utc_now

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


def bearer_token(authorization: str | None) -> str | None:
    if authorization is None:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def snapshot(record, store) -> dict:
    if record.absolute_deadline < record.idle_deadline:
        remaining = record.absolute_deadline - store.clock.now_monotonic()
    else:
        remaining = record.idle_deadline - store.clock.now_monotonic()

    now = utc_now()
    expires_at = now.fromtimestamp(
        now.timestamp() + max(0.0, remaining),
        tz=now.tzinfo,
    )
    absolute_remaining = max(
        0.0,
        record.absolute_deadline - store.clock.now_monotonic(),
    )
    absolute_expires_at = now.fromtimestamp(
        now.timestamp() + absolute_remaining,
        tz=now.tzinfo,
    )

    items = record.items
    text = derive_text(record.mode, items)
    updated_at = record.updated_at or now

    return {
        "session_id": record.session_id,
        "mode": record.mode,
        "status": record.status,
        "state_version": record.state_version,
        "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
        "absolute_expires_at": absolute_expires_at.isoformat().replace(
            "+00:00",
            "Z",
        ),
        "idle_timeout_seconds": store.idle_timeout_seconds,
        "reconnect_grace_seconds": store.reconnect_grace_seconds,
        "model_version": record.model_version,
        "stream_id": record.stream_id,
        "recovery_enabled": record.recovery_enabled,
        "transcript": {
            "revision": record.transcript_revision,
            "items": items,
            "text": text,
            "updated_at": updated_at.isoformat().replace("+00:00", "Z"),
        },
    }


@router.post("", status_code=201)
async def create_session(request: Request, body: SessionCreateRequest):
    registry = request.app.state.adapter_registry
    if not registry.readiness().get(body.mode, False):
        error = build_error(
            "MODEL_UNAVAILABLE",
            "This recognition mode is unavailable.",
            retryable=True,
        )
        return JSONResponse(status_code=503, content=error.model_dump())

    try:
        record, token = request.app.state.session_store.create(
            body.mode,
            recovery_enabled=body.recovery_enabled,
        )
    except SessionLimitExceeded:
        error = build_error(
            "SESSION_LIMIT",
            "The server has reached its session capacity.",
            retryable=True,
        )
        return JSONResponse(status_code=429, content=error.model_dump())

    return JSONResponse(
        status_code=201,
        content={
            "session_token": token,
            "session": snapshot(
                record,
                request.app.state.session_store,
            ),
        },
    )


@router.get("/{session_id}")
async def read_session(
    request: Request,
    session_id: str,
    authorization: str | None = Header(default=None),
):
    token = bearer_token(authorization)
    if token is None:
        error = build_error(
            "CREDENTIAL_REQUIRED",
            "A bearer capability is required.",
        )
        return JSONResponse(status_code=401, content=error.model_dump())

    try:
        record = request.app.state.session_store.authenticate(
            session_id,
            token,
        )
    except (SessionNotFound, SessionExpired):
        error = build_error(
            "SESSION_NOT_FOUND",
            "The requested session was not found.",
        )
        return JSONResponse(status_code=404, content=error.model_dump())

    return {"session": snapshot(record, request.app.state.session_store)}


@router.post("/{session_id}/capture")
async def capture_session(
    request: Request,
    session_id: str,
    body: CaptureRequest,
    authorization: str | None = Header(default=None),
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
    ),
):
    token = bearer_token(authorization)
    if token is None:
        error = build_error(
            "CREDENTIAL_REQUIRED",
            "A bearer capability is required.",
        )
        return JSONResponse(status_code=401, content=error.model_dump())
    if idempotency_key is None:
        error = build_error(
            "VALIDATION_ERROR",
            "An Idempotency-Key header is required.",
        )
        return JSONResponse(status_code=422, content=error.model_dump())

    try:
        command_id = validate_uuid(idempotency_key)
    except (ValueError, AttributeError):
        error = build_error(
            "VALIDATION_ERROR",
            "Idempotency-Key must be a canonical UUID.",
        )
        return JSONResponse(status_code=422, content=error.model_dump())

    try:
        record = request.app.state.session_store.authenticate(
            session_id,
            token,
        )
    except (SessionNotFound, SessionExpired):
        error = build_error(
            "SESSION_NOT_FOUND",
            "The requested session was not found.",
        )
        return JSONResponse(status_code=404, content=error.model_dump())

    fingerprint = f"POST /api/v1/sessions/{session_id}/capture|{body.model_dump_json()}"

    async with record.lock:

        def operation():
            check_revision(record, body.expected_revision)
            check_state_version(record, body.expected_state_version)

            if record.status == "ended":
                raise ValueError("SESSION_ENDED")

            if body.action == "start":
                if record.status == "capturing":
                    raise ValueError("ALREADY_CAPTURING")
                if record.stream_id is not None:
                    raise ValueError("STALE_STREAM")
                stream = request.app.state.recognition_service.start_stream(record.mode)
                record.status = "capturing"
                record.stream_id = stream.stream_id
                record.state_version += 1
            else:
                if record.status != "capturing":
                    raise ValueError("PAUSE_NOT_CAPTURING")
                if record.stream_id is not None:
                    request.app.state.recognition_service.invalidate_stream(
                        record.stream_id
                    )
                record.status = "paused"
                record.stream_id = None
                record.state_version += 1

            record.updated_at = utc_now()
            request.app.state.session_store.touch_idle(record)
            return snapshot(record, request.app.state.session_store)

        try:
            result = record.command_cache.execute(command_id, fingerprint, operation)
        except IdempotencyConflict:
            error = build_error(
                "IDEMPOTENCY_CONFLICT",
                "This command ID was used for a different request.",
                retryable=False,
            )
            return JSONResponse(status_code=409, content=error.model_dump())
        except RevisionConflict:
            error = build_error(
                "REVISION_CONFLICT",
                "Refresh the session before retrying.",
                details={"current_revision": record.transcript_revision},
            )
            return JSONResponse(status_code=409, content=error.model_dump())
        except StateConflict:
            error = build_error(
                "STATE_CONFLICT",
                "Capture status changed. Refresh and retry.",
                details={"current_state_version": record.state_version},
            )
            return JSONResponse(status_code=409, content=error.model_dump())
        except ValueError as exc:
            code = str(exc)
            error = build_error(
                code,
                "The capture action is not valid in the current state.",
                retryable=False,
            )
            return JSONResponse(status_code=409, content=error.model_dump())

    return {"session": result}


@router.post("/{session_id}/confirm")
async def confirm_session(
    request: Request,
    session_id: str,
    body: ConfirmRequest,
    authorization: str | None = Header(default=None),
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
    ),
):
    token = bearer_token(authorization)
    if token is None:
        error = build_error(
            "CREDENTIAL_REQUIRED",
            "A bearer capability is required.",
        )
        return JSONResponse(status_code=401, content=error.model_dump())
    if idempotency_key is None:
        error = build_error(
            "VALIDATION_ERROR",
            "An Idempotency-Key header is required.",
        )
        return JSONResponse(status_code=422, content=error.model_dump())

    try:
        command_id = validate_uuid(idempotency_key)
    except (ValueError, AttributeError):
        error = build_error(
            "VALIDATION_ERROR",
            "Idempotency-Key must be a canonical UUID.",
        )
        return JSONResponse(status_code=422, content=error.model_dump())

    try:
        record = request.app.state.session_store.authenticate(
            session_id,
            token,
        )
    except (SessionNotFound, SessionExpired):
        error = build_error(
            "SESSION_NOT_FOUND",
            "The requested session was not found.",
        )
        return JSONResponse(status_code=404, content=error.model_dump())

    fingerprint = f"POST /api/v1/sessions/{session_id}/confirm|{body.model_dump_json()}"

    async with record.lock:

        def operation():
            check_revision(record, body.expected_revision)

            if record.status != "capturing":
                raise ValueError("CANDIDATE_UNAVAILABLE")
            if record.stream_id != body.stream_id:
                raise StaleStreamError

            prediction = request.app.state.recognition_service.consume_candidate(
                body.stream_id,
                body.candidate_id,
            )
            kind = "word" if record.mode == "word" else "letter"
            item = append_model_item(
                record,
                text=prediction.text or "",
                kind=kind,
                label_id=prediction.label_id or "",
                score=prediction.score,
                model_version=prediction.model_version,
                confirmed_by="manual",
            )
            return {
                "session": snapshot(
                    record,
                    request.app.state.session_store,
                ),
                "item_id": item["item_id"],
            }

        try:
            result = record.command_cache.execute(
                command_id,
                fingerprint,
                operation,
            )
        except IdempotencyConflict:
            error = build_error(
                "IDEMPOTENCY_CONFLICT",
                "This command ID was used for a different request.",
            )
            return JSONResponse(status_code=409, content=error.model_dump())
        except RevisionConflict:
            error = build_error(
                "REVISION_CONFLICT",
                "Refresh the session before retrying.",
                details={"current_revision": record.transcript_revision},
            )
            return JSONResponse(status_code=409, content=error.model_dump())
        except (StaleStreamError, ValueError):
            error = build_error(
                "CANDIDATE_UNAVAILABLE",
                "The candidate or stream is no longer available.",
            )
            return JSONResponse(status_code=409, content=error.model_dump())
        except TranscriptLimitExceeded:
            error = build_error(
                "TRANSCRIPT_LIMIT",
                "The transcript limit would be exceeded.",
            )
            return JSONResponse(status_code=409, content=error.model_dump())

    return result
