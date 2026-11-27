import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app


class AlphabetCatalogueStub:
    mode = "alphabet"
    model_version = "test-alphabet-v1"
    confirmation_policy = "manual"
    required_sample_fps = None
    window_samples = 1
    labels = (
        {"label_id": "ZA", "text": "ز", "kind": "letter"},
        {"label_id": "ALEF", "text": "أ", "kind": "letter"},
    )

    def predict(self, frames, times_ms):
        raise AssertionError("Catalogue routes must not run inference")

    def reset_stream(self, stream_id):
        raise AssertionError("Catalogue routes must not start recognition streams")


@pytest.fixture
def catalogue_app():
    settings = Settings(environment="test", max_jpeg_width=320, max_fps=8)
    return create_app(settings, load_models=False)


@pytest.mark.asyncio
async def test_models_reports_unavailable_and_available_modes(catalogue_app):
    async with AsyncClient(
        transport=ASGITransport(app=catalogue_app), base_url="http://test"
    ) as client:
        empty = await client.get("/api/v1/models")
        assert empty.status_code == 200, empty.text
        for entry in empty.json()["models"]:
            assert entry["ready"] is False
            assert entry["input"] is None
            assert entry["model_version"] == "unavailable"
            assert entry["confirmation_policy"] == "manual"
        catalogue_app.state.adapter_registry.register(
            "alphabet", AlphabetCatalogueStub()
        )
        one_mode = await client.get("/api/v1/models")

    assert one_mode.status_code == 200, one_mode.text
    alphabet, word = one_mode.json()["models"]
    assert alphabet == {
        "mode": "alphabet",
        "model_version": "test-alphabet-v1",
        "ready": True,
        "confirmation_policy": "manual",
        "input": {
            "format": "jpeg",
            "max_width": 320,
            "max_height": 480,
            "max_jpeg_bytes": 163840,
            "max_message_bytes": 262144,
            "max_fps": 8,
            "required_sample_fps": None,
            "window_samples": 1,
            "mirrored": False,
        },
        "transcript_limits": {"max_items": 2000, "max_characters": 20_000},
    }
    assert word["mode"] == "word"
    assert word["ready"] is False
    assert word["input"] is None


@pytest.mark.asyncio
async def test_vocabulary_returns_versioned_public_labels_in_stable_order(
    catalogue_app,
):
    adapter = AlphabetCatalogueStub()
    catalogue_app.state.adapter_registry.register("alphabet", adapter)
    async with AsyncClient(
        transport=ASGITransport(app=catalogue_app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/vocabulary?mode=alphabet")
        word = await client.get("/api/v1/vocabulary?mode=word")

    assert response.status_code == 200, response.text
    assert response.json() == {
        "mode": "alphabet",
        "model_version": "test-alphabet-v1",
        "labels": [
            {"label_id": "ALEF", "text": "أ", "kind": "letter"},
            {"label_id": "ZA", "text": "ز", "kind": "letter"},
        ],
    }
    assert adapter.labels[0]["label_id"] == "ZA"
    assert word.status_code == 503, word.text
    assert word.json()["error"]["code"] == "MODEL_UNAVAILABLE"


@pytest.mark.asyncio
async def test_vocabulary_rejects_invalid_query(catalogue_app):
    async with AsyncClient(
        transport=ASGITransport(app=catalogue_app), base_url="http://test"
    ) as client:
        for suffix in ("", "?mode=other", "?mode=word&other=1"):
            response = await client.get("/api/v1/vocabulary" + suffix)
            assert response.status_code == 422, response.text
            assert response.json()["error"]["code"] == "VALIDATION_ERROR"
