# Owner: Ali.

from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.schemas.common import ModelMode

router = APIRouter(prefix="/api/v1/health", tags=["health"])


class LivenessResponse(BaseModel):
    status: Literal["alive"]


class ReadinessResponse(BaseModel):
    ready: bool
    modes: dict[ModelMode, bool]
    required_modes: list[ModelMode]


@router.get("/live", response_model=LivenessResponse)
async def live():
    """
    Liveness endpoint to check if the application is running.
    Returns 200 OK if the application is alive.
    """
    return {"status": "alive"}


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={
        503: {
            "model": ReadinessResponse,
            "description": "A required mode is unavailable.",
        }
    },
)
async def ready(request: Request):
    """Report whether every required recognition mode is available."""
    required_modes = request.app.state.settings.required_modes
    modes = request.app.state.adapter_registry.readiness()
    is_ready = all(modes[mode] for mode in required_modes)
    result = {
        "ready": is_ready,
        "modes": modes,
        "required_modes": list(required_modes),
    }

    return JSONResponse(status_code=200 if is_ready else 503, content=result)
