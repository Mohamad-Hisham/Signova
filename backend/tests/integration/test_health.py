import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_live_health():
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
        "required_modes": ["alphabet", "word"],
    }
