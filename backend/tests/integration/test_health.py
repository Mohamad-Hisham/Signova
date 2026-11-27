from unittest.mock import Mock

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app
from app.models.base import ModelAdapter


@pytest.mark.asyncio
async def test_live_health():
    app = create_app(Settings(_env_file=None), load_models=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


@pytest.mark.asyncio
async def test_ready_health_without_models():
    app = create_app(Settings(_env_file=None), load_models=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "ready": False,
        "modes": {
            "alphabet": False,
            "word": False,
        },
        "required_modes": ["alphabet"],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("registered_modes", "required_modes", "status_code"),
    [
        (("alphabet",), ("alphabet", "word"), 503),
        (("alphabet",), ("alphabet",), 200),
        (("alphabet", "word"), ("alphabet", "word"), 200),
    ],
)
async def test_ready_health_tracks_registered_required_modes(
    registered_modes, required_modes, status_code
):
    app = create_app(
        Settings(_env_file=None, required_modes=required_modes), load_models=False
    )
    registry = app.state.adapter_registry
    adapter = Mock(spec=ModelAdapter)
    for mode in registered_modes:
        registry.register(mode, adapter)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/v1/health/ready")

    assert response.status_code == status_code
    assert response.json() == {
        "ready": status_code == 200,
        "modes": {mode: mode in registered_modes for mode in ("alphabet", "word")},
        "required_modes": list(required_modes),
    }
    assert adapter.mock_calls == []
