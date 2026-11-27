"""Shared session capability, mutation ordering and rate checks."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.services.commands import IdempotencyConflict, RevisionConflict, StateConflict
from app.services.rate_limits import take_request
from app.services.sessions import (
    SessionDeleted,
    SessionExpired,
    SessionNotFound,
    SessionRecord,
)
from app.utilities.errors import ApiError
from app.utilities.ids import validate_uuid

session_bearer = HTTPBearer(
    scheme_name="SessionToken",
    description="Paste the session_token returned by session creation.",
    auto_error=False,
)


def _bearer_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Security(session_bearer)
    ],
) -> str | None:
    return credentials.credentials if credentials is not None else None


Authorization = Annotated[str | None, Depends(_bearer_token)]


def require_session(
    request: Request, session_id: str, token: str | None
) -> SessionRecord:
    if not token:
        raise ApiError(
            401,
            "CREDENTIAL_REQUIRED",
            "A bearer capability is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return request.app.state.session_store.authenticate(session_id, token)
    except (SessionDeleted, SessionExpired, SessionNotFound) as exc:
        raise session_access_error(exc) from exc


def check_session_current(request: Request, record: SessionRecord) -> None:
    try:
        request.app.state.session_store.check_current(record)
    except (SessionDeleted, SessionExpired, SessionNotFound) as exc:
        raise session_access_error(exc) from exc


def session_access_error(exc: Exception) -> ApiError:
    if isinstance(exc, SessionExpired):
        return ApiError(410, "SESSION_EXPIRED", "This session has expired.")
    if isinstance(exc, SessionDeleted):
        return ApiError(410, "SESSION_DELETED", "This session was deleted.")
    return ApiError(404, "SESSION_NOT_FOUND", "The requested session was not found.")


def require_command_id(idempotency_key: str | None) -> str:
    try:
        return validate_uuid(idempotency_key or "")
    except ValueError as exc:
        raise ApiError(
            422,
            "VALIDATION_ERROR",
            "A canonical UUID Idempotency-Key header is required.",
            details={
                "fields": [{"path": "header.Idempotency-Key", "reason": "invalid UUID"}]
            },
        ) from exc


def limit_mutation(request: Request, record: SessionRecord) -> None:
    state = request.app.state
    retry_after = take_request(
        record.mutation_times,
        state.session_store.clock.now_monotonic(),
        state.settings.mutation_requests_per_minute,
    )
    if retry_after is not None:
        raise rate_limited(retry_after)


def rate_limited(retry_after: int) -> ApiError:
    return ApiError(
        429,
        "RATE_LIMITED",
        "Too many requests. Wait before retrying.",
        retryable=True,
        headers={"Retry-After": str(retry_after)},
    )


def require_open_session(record: SessionRecord) -> None:
    if record.status == "ended":
        raise ApiError(409, "SESSION_ENDED", "This session has ended.")


def execute_session_command(
    request: Request,
    record: SessionRecord,
    command_id: str,
    body: BaseModel,
    operation: Callable[[], dict],
    *,
    allow_ended_replay: bool = False,
) -> dict:
    """Check current state, replay cached success, or apply one fresh command under the lock."""
    check_session_current(request, record)
    if not allow_ended_replay:
        require_open_session(record)

    def new_command() -> dict:
        require_open_session(record)
        limit_mutation(request, record)
        return operation()

    fingerprint = f"{request.method} {request.url.path}|{body.model_dump_json()}"
    try:
        return record.command_cache.execute(command_id, fingerprint, new_command)
    except IdempotencyConflict as exc:
        raise ApiError(
            409,
            "IDEMPOTENCY_CONFLICT",
            "This command ID was used for a different request.",
        ) from exc
    except RevisionConflict as exc:
        raise ApiError(
            409,
            "REVISION_CONFLICT",
            "Refresh the session before retrying.",
            details={"current_revision": record.transcript_revision},
        ) from exc
    except StateConflict as exc:
        raise ApiError(
            409,
            "STATE_CONFLICT",
            "Session state changed. Refresh before retrying.",
            details={"current_state_version": record.state_version},
        ) from exc
