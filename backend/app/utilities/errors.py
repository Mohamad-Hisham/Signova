# Owner: Ali.

from typing import Any

from app.schemas.common import ErrorEnvelope
from app.utilities.ids import new_uuid


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        retryable: bool = False,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.envelope = build_error(code, message, retryable=retryable, details=details)
        self.headers = headers


def build_error(
    code: str,
    message: str,
    *,
    retryable: bool = False,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> ErrorEnvelope:
    return ErrorEnvelope(
        error={
            "code": code,
            "message": message,
            "retryable": retryable,
            "details": details or {},
        },
        request_id=request_id or new_uuid(),
    )
