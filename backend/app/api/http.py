"""REST request limits, cache headers and safe error responses."""

import logging
from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.utilities.errors import ApiError

logger = logging.getLogger(__name__)


def error_response(error: ApiError) -> JSONResponse:
    return JSONResponse(
        error.envelope.model_dump(mode="json"),
        status_code=error.status_code,
        headers=error.headers,
    )


async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
    return error_response(exc)


async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    fields = []
    for error in exc.errors():
        error_type = error["type"]
        location = error["loc"]
        if error_type == "extra_forbidden":
            location = location[:-1]
        if error_type == "json_invalid":
            location = ("body",)
        reason = {
            "extra_forbidden": "unknown field",
            "json_invalid": "invalid JSON",
            "missing": "required",
            "literal_error": "unsupported value",
            "int_type": "integer required",
            "bool_type": "boolean required",
            "string_type": "text required",
        }.get(error_type, "invalid value")
        fields.append({"path": ".".join(map(str, location)), "reason": reason})
    return error_response(
        ApiError(
            422,
            "VALIDATION_ERROR",
            "The request is invalid.",
            details={"fields": fields},
        )
    )


class ApiRequestMiddleware:
    def __init__(self, app: ASGIApp, body_limit: int):
        self.app = app
        self.body_limit = body_limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not scope["path"].startswith("/api/v1/"):
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        private = path == "/api/v1/sessions" or path.startswith("/api/v1/sessions/")
        responded = False

        async def output(message: Message) -> None:
            nonlocal responded
            if message["type"] == "http.response.start":
                responded = True
                if private:
                    MutableHeaders(scope=message)["Cache-Control"] = "no-store"
            await send(message)

        try:
            checked_receive = await self._receive_body(scope, receive)
            if checked_receive is not None:
                await self.app(scope, checked_receive, output)
        except ApiError as exc:
            await error_response(exc)(scope, receive, output)
        except Exception:
            if responded:
                raise
            logger.error("Unexpected REST request failure")
            error = ApiError(
                500, "INTERNAL_ERROR", "The request could not be completed."
            )
            await error_response(error)(scope, receive, output)

    async def _receive_body(
        self, scope: Scope, receive: Receive
    ) -> Callable[[], Awaitable[Message]] | None:
        method = scope["method"]
        if method not in {"GET", "DELETE", "POST", "PATCH"}:
            return receive

        no_body = method in {"GET", "DELETE"}
        headers = Headers(scope=scope)
        declared = headers.get("content-length", "")
        if (
            declared.isascii()
            and declared.isdecimal()
            and (len(declared) > 18 or int(declared) > self.body_limit)
        ):
            raise ApiError(413, "PAYLOAD_TOO_LARGE", "The request body is too large.")

        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return None
            part = message.get("body", b"")
            if part and no_body:
                raise ApiError(
                    422,
                    "VALIDATION_ERROR",
                    "This request must have an empty body.",
                    details={
                        "fields": [{"path": "body", "reason": "body is not allowed"}]
                    },
                )
            if len(body) + len(part) > self.body_limit:
                raise ApiError(
                    413, "PAYLOAD_TOO_LARGE", "The request body is too large."
                )
            body.extend(part)
            if not message.get("more_body", False):
                break

        media_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if body and media_type != "application/json":
            raise ApiError(
                422,
                "VALIDATION_ERROR",
                "Use an application/json request body.",
                details={
                    "fields": [
                        {"path": "header.Content-Type", "reason": "expected JSON"}
                    ]
                },
            )
        if body:
            try:
                body.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ApiError(
                    422,
                    "VALIDATION_ERROR",
                    "The JSON body must use UTF-8.",
                    details={"fields": [{"path": "body", "reason": "invalid UTF-8"}]},
                ) from exc

        pending = True

        async def replay() -> Message:
            nonlocal pending
            if pending:
                pending = False
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        return replay
