from typing import Any

from app.schemas.common import ErrorEnvelope
from app.utilities.ids import new_uuid


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
