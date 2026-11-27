from unittest.mock import Mock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app
from app.models.base import ModelAdapter
from app.utilities.time import Clock


@pytest.mark.asyncio
async def test_readable_validation_without_rejected_values():
    app = create_app(Settings(_env_file=None), load_models=False)
    private = "private marker"
    cases = [
        ({"mode": private}, {"path": "body.mode", "reason": "unsupported value"}),
        (
            {"mode": "word", private: "sensitive"},
            {"path": "body", "reason": "unknown field"},
        ),
        (
            {"mode": "word", "recovery_enabled": "false"},
            {"path": "body.recovery_enabled", "reason": "boolean required"},
        ),
    ]
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        for payload, field in cases:
            response = await client.post("/api/v1/sessions", json=payload)
            assert response.status_code == 422
            assert response.headers["cache-control"] == "no-store"
            assert response.json()["error"]["details"]["fields"] == [field]
            assert private not in response.text
        response = await client.post(
            "/api/v1/sessions",
            content=b'{"mode":',
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["details"]["fields"] == [
            {"path": "body", "reason": "invalid JSON"}
        ]
        wrong_media_type = await client.post(
            "/api/v1/sessions", content=b'{"mode":"word"}'
        )
        assert wrong_media_type.status_code == 422
        assert wrong_media_type.json()["error"]["code"] == "VALIDATION_ERROR"
        bad_encoding = await client.post(
            "/api/v1/sessions",
            content=b'{"mode":"\xff"}',
            headers={"Content-Type": "application/json"},
        )
        assert bad_encoding.status_code == 422
        assert bad_encoding.json()["error"]["details"]["fields"] == [
            {"path": "body", "reason": "invalid UTF-8"}
        ]


@pytest.mark.asyncio
async def test_http_body_limit_checks_declared_and_chunked_bytes():
    app = create_app(
        Settings(_env_file=None, max_rest_body_bytes=32), load_models=False
    )

    async def oversized_chunks():
        yield b" " * 30
        yield b" " * 5

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        for content in (b" " * 33, oversized_chunks()):
            response = await client.post(
                "/api/v1/sessions",
                content=content,
                headers={"Content-Type": "application/json"},
            )
            assert response.status_code == 413
            assert response.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"
        response = await client.request("GET", "/api/v1/models", json={})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_creation_and_fresh_mutation_limits_preserve_exact_replays():
    now = [0.0]
    app = create_app(
        Settings(
            _env_file=None,
            creation_requests_per_minute=1,
            mutation_requests_per_minute=1,
        ),
        clock=Clock(lambda: now[0]),
        load_models=False,
    )
    app.state.adapter_registry.register(
        "alphabet", Mock(spec=ModelAdapter, model_version="alphabet-test")
    )
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post("/api/v1/sessions", json={"mode": "alphabet"})
        assert created.status_code == 201
        repeated_creation = await client.post(
            "/api/v1/sessions", json={"mode": "alphabet"}
        )
        assert repeated_creation.status_code == 429
        assert repeated_creation.headers["retry-after"] == "60"
        assert repeated_creation.json()["error"]["code"] == "RATE_LIMITED"

        payload = created.json()
        path = f"/api/v1/sessions/{payload['session']['session_id']}/transcript"
        headers = {
            "Authorization": f"Bearer {payload['session_token']}",
            "Idempotency-Key": str(uuid4()),
        }
        body = {"expected_revision": 0, "items": [{"text": "س"}]}
        edited = await client.patch(path, headers=headers, json=body)
        assert edited.status_code == 200
        assert (
            await client.patch(path, headers=headers, json=body)
        ).json() == edited.json()
        headers["Idempotency-Key"] = str(uuid4())
        body["expected_revision"] = 1
        limited = await client.patch(path, headers=headers, json=body)
        assert limited.status_code == 429
        assert limited.headers["retry-after"] == "60"
        now[0] = 60
        assert (await client.patch(path, headers=headers, json=body)).status_code == 200
        assert (
            await client.post("/api/v1/sessions", json={"mode": "alphabet"})
        ).status_code == 201


@pytest.mark.asyncio
async def test_exact_cors_preflight_includes_session_headers():
    app = create_app(Settings(_env_file=None), load_models=False)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "Authorization, Idempotency-Key, Content-Type",
        }
        allowed = await client.options(
            "/api/v1/sessions/example/transcript", headers=headers
        )
        assert allowed.status_code == 200
        assert allowed.headers["access-control-allow-origin"] == headers["Origin"]
        headers["Origin"] = "http://localhost:5173.example.invalid"
        denied = await client.options(
            "/api/v1/sessions/example/transcript", headers=headers
        )
        assert denied.status_code == 400
        assert "access-control-allow-origin" not in denied.headers
