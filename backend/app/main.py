# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve the one FastAPI application composition and lifecycle boundary.
# Owner: Hisham.
# Expected inputs: Reviewed server settings and both trusted approved inference packages.
# Expected outputs: Future application lifecycle and per-mode readiness; no app object exists
#   yet.
# Responsibilities: Verify artifacts/runtimes, load once, warmup/golden check, attach
#   routes/socket/services and start bounded cleanup ownership.
# Connections: config.py, api/, ws/live.py, model adapters and sessions service.
# Future implementation: Implement startup/shutdown composition only after runtime and
#   implementation authorization.
# Rules and limitations: One process/worker/replica; no model download/import-time training,
#   request-local loads or fake readiness fallback.
# Expected tests or acceptance: Missing/corrupt artifact leaves mode unready; lifespan loads
#   once; shutdown drops session/model resources without disk dumps.

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.transcript import router as transcript_router
from app.config import get_settings
from app.models.base import AdapterRegistry
from app.services.recognition import RecognitionService
from app.services.sessions import SessionStore
from app.utilities.time import Clock

settings = get_settings()
adapter_registry = AdapterRegistry()
session_store = SessionStore(
    Clock(),
    idle_timeout_seconds=settings.idle_timeout_seconds,
    absolute_timeout_seconds=settings.absolute_timeout_seconds,
    reconnect_grace_seconds=settings.reconnect_grace_seconds,
    max_sessions=settings.max_sessions,
)
recognition_service = RecognitionService(Clock(), {})


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Placeholder for startup logic: verify artifacts, warmup, attach routes/services.
    print("Starting up the Signova application...")

    yield

    # Placeholder for shutdown logic: cleanup resources, close sessions.
    print("Shutting down the Signova application...")


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.state.adapter_registry = adapter_registry
app.state.session_store = session_store
app.state.recognition_service = recognition_service
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    expose_headers=["X-Transcript-Revision"],
)
app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(transcript_router)
