# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve public /api/v1/health/live and /health/ready REST boundaries.
# Owner: Ali.
# Expected inputs: Application liveness and trusted per-mode startup/golden readiness state.
# Expected outputs: Future alive 200 or ready 200/503 with documented non-error readiness shape.
# Responsibilities: Keep process liveness separate from release-required model availability
#   without invoking inference per health request.
# Connections: main lifecycle, config release-required modes and model registry readiness.
# Future implementation: Implement thin route serialization during backend work.
# Rules and limitations: No artifact filesystem paths, secrets, fake substitutions or model
#   computation in liveness.
# Expected tests or acceptance: Unready required mode returns 503 with
#   ready/modes/required_modes; live can remain 200.

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import get_settings

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/live")
async def live():
    """
    Liveness endpoint to check if the application is running.
    Returns 200 OK if the application is alive.
    """
    return {"status": "alive"}


@router.get("/ready")
async def ready():
    """
    Readiness endpoint to check if the application is ready to serve requests.
    Returns 200 OK if the application is ready, or 503 Service Unavailable if not.
    """
    # Placeholder for readiness logic: check if required modes are ready.
    # In a real implementation, you would check the actual readiness state here.

    settings = get_settings()
    required_modes = list(settings.required_modes)
    result = {
        "ready": False,
        "modes": {"alphabet": False, "word": False},
        "required_modes": required_modes,
    }

    return JSONResponse(status_code=503, content=result)
