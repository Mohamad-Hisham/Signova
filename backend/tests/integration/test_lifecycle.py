from unittest.mock import Mock

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.config import (
    LOCAL_ALPHABET_CHECKPOINT_SHA256,
    LOCAL_ALPHABET_HAND_MODEL_SHA256,
    Settings,
)
from app.main import create_app
from app.models.alphabet import AlphabetAdapter


@pytest.mark.asyncio
async def test_registration_and_model_cleanup_follow_app_lifespan(monkeypatch):
    adapter = Mock(spec=AlphabetAdapter, model_version="test-alphabet")
    load = Mock(return_value=adapter)
    monkeypatch.setattr(AlphabetAdapter, "load", load)
    settings = Settings(_env_file=None)
    app = create_app(settings)
    assert app.state.adapter_registry.readiness() == {"alphabet": False, "word": False}
    async with app.router.lifespan_context(app):
        assert app.state.adapter_registry.get("alphabet") is adapter
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            for _ in range(2):
                response = await client.get("/api/v1/health/ready")
                assert response.status_code == 200
                assert response.json()["modes"] == {"alphabet": True, "word": False}
    load.assert_called_once_with(
        settings.alphabet_checkpoint,
        settings.alphabet_hand_model,
        checkpoint_sha256=LOCAL_ALPHABET_CHECKPOINT_SHA256,
        hand_model_sha256=LOCAL_ALPHABET_HAND_MODEL_SHA256,
    )
    adapter.close.assert_called_once_with()
    assert app.state.adapter_registry.readiness() == {"alphabet": False, "word": False}


@pytest.mark.asyncio
async def test_missing_artifact_keeps_health_live_and_alphabet_unready(tmp_path):
    missing = tmp_path / "missing.pth"
    app = create_app(Settings(_env_file=None, alphabet_checkpoint=missing))
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        assert (await client.get("/api/v1/health/live")).status_code == 200
        ready = await client.get("/api/v1/health/ready")
        assert ready.status_code == 503
        assert ready.json()["modes"] == {"alphabet": False, "word": False}
        assert str(missing) not in ready.text


@pytest.mark.parametrize(
    "fields",
    [
        {"cors_origins": ("*",)},
        {"cors_origins": ("http://host/path",)},
        {"cors_origins": ("http://host:100000",)},
        {"required_modes": ("alphabet", "alphabet")},
        {"max_jpeg_bytes": 163_841},
    ],
)
def test_rejects_configuration_that_exceeds_contract(fields):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **fields)
