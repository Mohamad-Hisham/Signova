"""Authenticated transcript mutations and current-revision TXT export."""

from collections.abc import Callable
from typing import Annotated, Literal

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import PlainTextResponse
from pydantic import field_validator

from app.api.session_access import (
    check_session_current,
    execute_session_command,
    require_command_id,
    require_session,
)
from app.api.sessions import (
    ACCESS_RESPONSES,
    MUTATION_RESPONSES,
    VALIDATION_RESPONSE,
    Authorization,
    CommandKey,
    snapshot,
)
from app.schemas.rest import (
    ExportQuery,
    SessionResponse,
    SpaceRequest,
    TranscriptClearRequest,
    TranscriptReplaceRequest,
)
from app.services.commands import RevisionConflict, check_revision
from app.services.sessions import SessionRecord
from app.services.transcript import (
    CaptureActiveError,
    InvalidTranscriptItem,
    SpaceNotAllowedError,
    TranscriptLimitExceeded,
    WrongModeError,
    append_space,
    clear_transcript,
    derive_text,
    replace_transcript,
)
from app.utilities.errors import ApiError

TranscriptCommand = SpaceRequest | TranscriptClearRequest | TranscriptReplaceRequest
TranscriptCause = Literal["space", "replace", "clear"]

router = APIRouter(
    prefix="/api/v1/sessions/{session_id}",
    tags=["transcript"],
)


class ExportParameters(ExportQuery):
    @field_validator("revision", mode="before")
    @classmethod
    def decode_decimal_revision(cls, value: object) -> object:
        if isinstance(value, str) and value.isascii() and value.isdecimal():
            return int(value)
        return value


def _revision_conflict(record: SessionRecord) -> ApiError:
    return ApiError(
        409,
        "REVISION_CONFLICT",
        "Refresh the session before retrying.",
        details={"current_revision": record.transcript_revision},
    )


def _ensure_mutable(record: SessionRecord) -> None:
    if record.status == "disconnected":
        raise ApiError(
            409,
            "STATE_CONFLICT",
            "Reconnect the session before changing the transcript.",
            details={"current_state_version": record.state_version},
        )


async def _mutate(
    request: Request,
    session_id: str,
    body: TranscriptCommand,
    authorization: str | None,
    idempotency_key: str | None,
    *,
    cause: TranscriptCause,
    change: Callable[[SessionRecord], None],
) -> dict:
    record = require_session(request, session_id, authorization)
    command_id = require_command_id(idempotency_key)
    store = request.app.state.session_store
    applied = False
    async with record.lock:

        def operation():
            nonlocal applied
            check_revision(record, body.expected_revision)
            _ensure_mutable(record)
            change(record)
            if cause == "clear":
                if record.stream_id is not None:
                    request.app.state.recognition_service.invalidate_stream(
                        record.stream_id
                    )
                record.status = "paused"
                record.stream_id = None
                record.recovery_enabled = False
                record.state_version += 1
                record.command_cache.purge()
            store.touch_idle(record)
            applied = True
            return {"session": snapshot(record, store)}

        try:
            result = execute_session_command(
                request, record, command_id, body, operation
            )
        except WrongModeError as exc:
            raise ApiError(
                409, "WRONG_MODE", "Space is only allowed in alphabet mode."
            ) from exc
        except CaptureActiveError as exc:
            raise ApiError(
                409, "CAPTURE_ACTIVE", "Pause capture before changing the transcript."
            ) from exc
        except SpaceNotAllowedError as exc:
            raise ApiError(409, "SPACE_NOT_ALLOWED", str(exc)) from exc
        except InvalidTranscriptItem as exc:
            raise ApiError(
                422,
                "VALIDATION_ERROR",
                "The replacement contains an invalid item.",
                details={"fields": [{"path": exc.path, "reason": str(exc)}]},
            ) from exc
        except TranscriptLimitExceeded as exc:
            raise ApiError(
                409, "TRANSCRIPT_LIMIT", "The transcript would exceed its limits."
            ) from exc

        if applied:
            live = request.app.state.live
            live.publish(
                record,
                "transcript.updated",
                {
                    "session": result["session"],
                    "cause": cause,
                    "command_id": command_id,
                    "committed_item_id": None,
                },
                discard_pending=cause == "clear",
            )
            if cause == "clear":
                live.publish(
                    record,
                    "session.state",
                    {"session": result["session"], "reason": "pause"},
                )
    return result


@router.post("/space", response_model=SessionResponse, responses=MUTATION_RESPONSES)
async def add_space(
    request: Request,
    session_id: str,
    body: SpaceRequest,
    authorization: Authorization = None,
    idempotency_key: CommandKey = None,
):
    """Append one explicit space while alphabet capture is paused."""
    return await _mutate(
        request,
        session_id,
        body,
        authorization,
        idempotency_key,
        cause="space",
        change=lambda record: append_space(record, body.expected_revision),
    )


@router.patch(
    "/transcript", response_model=SessionResponse, responses=MUTATION_RESPONSES
)
async def replace_session_transcript(
    request: Request,
    session_id: str,
    body: TranscriptReplaceRequest,
    authorization: Authorization = None,
    idempotency_key: CommandKey = None,
):
    """Replace the whole confirmed item list while capture is paused."""
    replacements = [item.model_dump() for item in body.items]
    return await _mutate(
        request,
        session_id,
        body,
        authorization,
        idempotency_key,
        cause="replace",
        change=lambda record: replace_transcript(
            record, body.expected_revision, replacements
        ),
    )


@router.post(
    "/transcript/clear",
    response_model=SessionResponse,
    responses=MUTATION_RESPONSES,
)
async def clear_session_transcript(
    request: Request,
    session_id: str,
    body: TranscriptClearRequest,
    authorization: Authorization = None,
    idempotency_key: CommandKey = None,
):
    """Remove confirmed text and active capture evidence."""
    return await _mutate(
        request,
        session_id,
        body,
        authorization,
        idempotency_key,
        cause="clear",
        change=lambda record: clear_transcript(record, body.expected_revision),
    )


@router.get(
    "/export",
    response_class=PlainTextResponse,
    responses={
        **ACCESS_RESPONSES,
        **VALIDATION_RESPONSE,
        204: {"description": "The transcript is empty"},
        409: MUTATION_RESPONSES[409],
    },
)
async def export_session_transcript(
    request: Request,
    session_id: str,
    query: Annotated[ExportParameters, Query()],
    authorization: Authorization = None,
):
    """Download the exact confirmed text at the requested revision."""
    record = require_session(request, session_id, authorization)
    async with record.lock:
        check_session_current(request, record)
        try:
            check_revision(record, query.revision)
        except RevisionConflict as exc:
            raise _revision_conflict(record) from exc
        text = derive_text(record.mode, record.items)
        headers = {
            "Content-Disposition": 'attachment; filename="signova-transcript.txt"',
            "Content-Type": "text/plain; charset=utf-8",
            "Cache-Control": "no-store",
            "X-Transcript-Revision": str(record.transcript_revision),
        }
    if not text:
        return Response(status_code=204, headers=headers)
    return PlainTextResponse(text, headers=headers)
