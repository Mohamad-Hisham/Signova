"""Single-process FastAPI application and model lifecycle."""

import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.catalog import router as catalogue_router
from app.api.health import router as health_router
from app.api.http import (
    ApiRequestMiddleware,
    api_error_handler,
    validation_error_handler,
)
from app.api.sessions import router as sessions_router
from app.api.transcript import router as transcript_router
from app.config import (
    LOCAL_ALPHABET_CHECKPOINT,
    LOCAL_ALPHABET_CHECKPOINT_SHA256,
    LOCAL_ALPHABET_HAND_MODEL,
    LOCAL_ALPHABET_HAND_MODEL_SHA256,
    Settings,
    get_settings,
)
from app.models.alphabet import AlphabetAdapter
from app.models.base import AdapterRegistry
from app.services.rate_limits import CreationRateLimiter
from app.services.recognition import RecognitionService
from app.services.sessions import SessionRecord, SessionStore, TerminalReason
from app.utilities.errors import ApiError
from app.utilities.time import Clock
from app.ws.live import WebSocketHub
from app.ws.live import router as live_router

logger = logging.getLogger(__name__)


async def _load_alphabet(settings: Settings) -> AlphabetAdapter | None:
    checkpoint_digest = settings.alphabet_checkpoint_sha256
    if (
        checkpoint_digest is None
        and settings.alphabet_checkpoint == LOCAL_ALPHABET_CHECKPOINT
    ):
        checkpoint_digest = LOCAL_ALPHABET_CHECKPOINT_SHA256
    hand_digest = settings.alphabet_hand_model_sha256
    if (
        hand_digest is None
        and settings.alphabet_hand_model == LOCAL_ALPHABET_HAND_MODEL
    ):
        hand_digest = LOCAL_ALPHABET_HAND_MODEL_SHA256

    try:
        return await asyncio.to_thread(
            AlphabetAdapter.load,
            settings.alphabet_checkpoint,
            settings.alphabet_hand_model,
            checkpoint_sha256=checkpoint_digest,
            hand_model_sha256=hand_digest,
        )
    except Exception as exc:  # noqa: BLE001 - native runtime failures leave the mode unready
        logger.warning(
            "Alphabet model unavailable during startup (%s)", type(exc).__name__
        )
        return None


def create_app(
    settings: Settings | None = None,
    *,
    clock: Clock | None = None,
    load_models: bool = True,
) -> FastAPI:
    settings = settings or get_settings()
    clock = clock or Clock()
    registry = AdapterRegistry()
    recognition = RecognitionService(clock, registry)
    live = WebSocketHub()
    creation_rate = CreationRateLimiter(clock, settings.creation_requests_per_minute)

    def terminate(record: SessionRecord, reason: TerminalReason) -> None:
        if record.stream_id is not None:
            recognition.invalidate_stream(record.stream_id)
        event_type = "session.deleted" if reason == "user" else "session.expired"
        live.publish(
            record,
            event_type,
            {"reason": reason},
            discard_pending=True,
            close_code=1000,
        )

    store = SessionStore(
        clock,
        idle_timeout_seconds=settings.idle_timeout_seconds,
        absolute_timeout_seconds=settings.absolute_timeout_seconds,
        reconnect_grace_seconds=settings.reconnect_grace_seconds,
        end_review_seconds=settings.end_review_seconds,
        max_sessions=settings.max_sessions,
        on_terminate=terminate,
    )

    async def sweep() -> None:
        while True:
            await asyncio.sleep(settings.sweep_interval_seconds)
            store.sweep_expired()
            creation_rate.sweep(clock.now_monotonic())

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        alphabet = await _load_alphabet(settings) if load_models else None
        if alphabet is not None:
            registry.register("alphabet", alphabet)
        cleanup = asyncio.create_task(sweep())
        try:
            yield
        finally:
            cleanup.cancel()
            with suppress(asyncio.CancelledError):
                await cleanup
            live.close_all()
            store.shutdown()
            await recognition.shutdown()
            if alphabet is not None:
                registry.unregister("alphabet")
                await asyncio.to_thread(alphabet.close)

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.settings = settings
    app.state.adapter_registry = registry
    app.state.session_store = store
    app.state.recognition_service = recognition
    app.state.live = live
    app.state.creation_rate = creation_rate
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_middleware(ApiRequestMiddleware, body_limit=settings.max_rest_body_bytes)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
        expose_headers=["X-Transcript-Revision"],
    )
    app.include_router(health_router)
    app.include_router(catalogue_router)
    app.include_router(sessions_router)
    app.include_router(transcript_router)
    app.include_router(live_router)
    return app


app = create_app()
