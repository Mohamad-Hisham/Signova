# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve replacement, clear and current-revision TXT export REST boundaries.
# Owner: Ali.
# Expected inputs: Bearer capability, validated edit/clear commands or format/revision query.
# Expected outputs: Future canonical snapshots or UTF-8 no-store text/204 export.
# Responsibilities: Delegate atomic validation/replacement/clear to service, attach correct
#   export headers and safe conflicts.
# Connections: transcript/sessions/commands services and strict REST/common schemas.
# Future implementation: Implement thin HTTP behavior after transcript and lifecycle decisions
#   are agreed.
# Rules and limitations: No server export file, permanent history, arbitrary format, partial
#   edit or client provenance acceptance.
# Expected tests or acceptance: 204 empty export, 409 stale revision, exact headers, paused
#   replacement and clear-during-inference match contract.

from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse

from app.api.sessions import bearer_token, snapshot
from app.schemas.rest import (
    SpaceRequest,
    TranscriptClearRequest,
    TranscriptReplaceRequest,
)
from app.services.commands import (
    IdempotencyConflict,
    RevisionConflict,
)
from app.services.sessions import SessionExpired, SessionNotFound
from app.services.transcript import (
    CaptureActiveError,
    TranscriptLimitExceeded,
    WrongModeError,
    append_space,
    clear_transcript,
    replace_transcript,
)
from app.utilities.errors import build_error
from app.utilities.ids import validate_uuid

router = APIRouter(
    prefix="/api/v1/sessions/{session_id}",
    tags=["transcript"],
)


def _authenticate(
    request: Request,
    session_id: str,
    authorization: str | None,
):
    token = bearer_token(authorization)
    if token is None:
        return None, JSONResponse(
            status_code=401,
            content=build_error(
                "CREDENTIAL_REQUIRED",
                "A bearer capability is required.",
            ).model_dump(),
        )
    try:
        record = request.app.state.session_store.authenticate(
            session_id,
            token,
        )
    except (SessionNotFound, SessionExpired):
        return None, JSONResponse(
            status_code=404,
            content=build_error(
                "SESSION_NOT_FOUND",
                "The requested session was not found.",
            ).model_dump(),
        )
    return record, None


def _command_id(idempotency_key: str | None):
    if idempotency_key is None:
        return None, JSONResponse(
            status_code=422,
            content=build_error(
                "VALIDATION_ERROR",
                "An Idempotency-Key header is required.",
            ).model_dump(),
        )
    try:
        return validate_uuid(idempotency_key), None
    except (ValueError, AttributeError):
        return None, JSONResponse(
            status_code=422,
            content=build_error(
                "VALIDATION_ERROR",
                "Idempotency-Key must be a canonical UUID.",
            ).model_dump(),
        )


@router.post("/space")
async def add_space(
    request: Request,
    session_id: str,
    body: SpaceRequest,
    authorization: str | None = Header(default=None),
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
    ),
):
    record, failure = _authenticate(request, session_id, authorization)
    if failure is not None:
        return failure
    command_id, failure = _command_id(idempotency_key)
    if failure is not None:
        return failure

    fingerprint = f"POST /api/v1/sessions/{session_id}/space|{body.model_dump_json()}"
    async with record.lock:

        def operation():
            append_space(record, body.expected_revision)
            return {"session": snapshot(record, request.app.state.session_store)}

        try:
            result = record.command_cache.execute(
                command_id,
                fingerprint,
                operation,
            )
        except IdempotencyConflict:
            return JSONResponse(
                status_code=409,
                content=build_error(
                    "IDEMPOTENCY_CONFLICT",
                    "This command ID was used for a different request.",
                ).model_dump(),
            )
        except RevisionConflict:
            return JSONResponse(
                status_code=409,
                content=build_error(
                    "REVISION_CONFLICT",
                    "Refresh the session before retrying.",
                    details={"current_revision": record.transcript_revision},
                ).model_dump(),
            )
        except WrongModeError:
            return JSONResponse(
                status_code=409,
                content=build_error(
                    "WRONG_MODE",
                    "Space is only allowed in alphabet mode.",
                ).model_dump(),
            )
        except CaptureActiveError:
            return JSONResponse(
                status_code=409,
                content=build_error(
                    "CAPTURE_ACTIVE",
                    "Pause capture before changing the transcript.",
                ).model_dump(),
            )
        except ValueError as exc:
            return JSONResponse(
                status_code=409,
                content=build_error(
                    "SPACE_NOT_ALLOWED",
                    str(exc),
                ).model_dump(),
            )

    return result


@router.patch("/transcript")
async def replace_session_transcript(
    request: Request,
    session_id: str,
    body: TranscriptReplaceRequest,
    authorization: str | None = Header(default=None),
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
    ),
):
    record, failure = _authenticate(request, session_id, authorization)
    if failure is not None:
        return failure
    command_id, failure = _command_id(idempotency_key)
    if failure is not None:
        return failure

    fingerprint = (
        f"PATCH /api/v1/sessions/{session_id}/transcript|{body.model_dump_json()}"
    )
    async with record.lock:

        def operation():
            replacements = [item.model_dump(exclude_none=False) for item in body.items]
            replace_transcript(
                record,
                body.expected_revision,
                replacements,
            )
            return {"session": snapshot(record, request.app.state.session_store)}

        try:
            result = record.command_cache.execute(
                command_id,
                fingerprint,
                operation,
            )
        except IdempotencyConflict:
            return JSONResponse(
                status_code=409,
                content=build_error(
                    "IDEMPOTENCY_CONFLICT",
                    "This command ID was used for a different request.",
                ).model_dump(),
            )
        except RevisionConflict:
            return JSONResponse(
                status_code=409,
                content=build_error(
                    "REVISION_CONFLICT",
                    "Refresh the session before retrying.",
                    details={"current_revision": record.transcript_revision},
                ).model_dump(),
            )
        except CaptureActiveError:
            return JSONResponse(
                status_code=409,
                content=build_error(
                    "CAPTURE_ACTIVE",
                    "Pause capture before changing the transcript.",
                ).model_dump(),
            )
        except (TranscriptLimitExceeded, ValueError) as exc:
            code = (
                "TRANSCRIPT_LIMIT"
                if isinstance(exc, TranscriptLimitExceeded)
                else "VALIDATION_ERROR"
            )
            status = 409 if code == "TRANSCRIPT_LIMIT" else 422
            return JSONResponse(
                status_code=status,
                content=build_error(
                    code,
                    str(exc),
                ).model_dump(),
            )

    return result


@router.post("/transcript/clear")
async def clear_session_transcript(
    request: Request,
    session_id: str,
    body: TranscriptClearRequest,
    authorization: str | None = Header(default=None),
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
    ),
):
    record, failure = _authenticate(request, session_id, authorization)
    if failure is not None:
        return failure
    command_id, failure = _command_id(idempotency_key)
    if failure is not None:
        return failure

    fingerprint = (
        f"POST /api/v1/sessions/{session_id}/transcript/clear|{body.model_dump_json()}"
    )
    async with record.lock:

        def operation():
            clear_transcript(record, body.expected_revision)
            if record.status == "capturing":
                record.status = "paused"
                if record.stream_id is not None:
                    request.app.state.recognition_service.invalidate_stream(
                        record.stream_id
                    )
                record.stream_id = None
                record.state_version += 1
            record.command_cache.purge()
            return {"session": snapshot(record, request.app.state.session_store)}

        try:
            result = record.command_cache.execute(
                command_id,
                fingerprint,
                operation,
            )
        except IdempotencyConflict:
            return JSONResponse(
                status_code=409,
                content=build_error(
                    "IDEMPOTENCY_CONFLICT",
                    "This command ID was used for a different request.",
                ).model_dump(),
            )
        except RevisionConflict:
            return JSONResponse(
                status_code=409,
                content=build_error(
                    "REVISION_CONFLICT",
                    "Refresh the session before retrying.",
                    details={"current_revision": record.transcript_revision},
                ).model_dump(),
            )

    return result
