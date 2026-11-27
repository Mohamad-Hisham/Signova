from unittest.mock import Mock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app
from app.models.base import ModelAdapter
from app.utilities.time import Clock


@pytest.fixture
def app():
    return create_app(Settings(_env_file=None), load_models=False)


def register(app, mode):
    adapter = Mock(spec=ModelAdapter, model_version=f"{mode}-test-v1")
    app.state.adapter_registry.register(mode, adapter)
    return adapter


async def create_alphabet_session(client):
    response = await client.post("/api/v1/sessions", json={"mode": "alphabet"})
    assert response.status_code == 201, response.text
    payload = response.json()
    return (
        f"/api/v1/sessions/{payload['session']['session_id']}",
        {"Authorization": f"Bearer {payload['session_token']}"},
    )


def command(access, key=None):
    return {**access, "Idempotency-Key": key or str(uuid4())}


def error_code(response, status, code):
    assert response.status_code == status, response.text
    assert response.json()["error"]["code"] == code


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["alphabet", "word"])
async def test_create_and_read_session(app, mode):
    adapter = register(app, mode)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post("/api/v1/sessions", json={"mode": mode})

        assert created.status_code == 201
        assert created.headers["cache-control"] == "no-store"
        payload = created.json()
        assert set(payload) == {"session_token", "session"}
        session = payload["session"]
        assert session["mode"] == mode
        assert session["model_version"] == adapter.model_version
        assert session["status"] == "paused"
        assert session["state_version"] == 0
        assert session["stream_id"] is None
        assert session["recovery_enabled"] is False
        assert session["transcript"]["revision"] == 0
        assert session["transcript"]["text"] == ""
        assert session["transcript"]["items"] == []

        path = f"/api/v1/sessions/{session['session_id']}"
        token = payload["session_token"]
        read = await client.get(path, headers={"Authorization": f"Bearer {token}"})
        assert read.status_code == 200
        assert read.headers["cache-control"] == "no-store"
        assert set(read.json()) == {"session"}
        returned = read.json()["session"]
        assert returned["session_id"] == session["session_id"]
        assert returned["model_version"] == adapter.model_version
        assert returned["transcript"] == session["transcript"]

        missing = await client.get(path)
        assert missing.status_code == 401
        assert missing.json()["error"]["code"] == "CREDENTIAL_REQUIRED"

        wrong = await client.get(path, headers={"Authorization": "Bearer wrong-token"})
        assert wrong.status_code == 404
        assert wrong.json()["error"]["code"] == "SESSION_NOT_FOUND"

    assert adapter.mock_calls == []


@pytest.mark.asyncio
async def test_create_session_for_unavailable_mode(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/sessions", json={"mode": "alphabet"})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "MODEL_UNAVAILABLE"


@pytest.mark.asyncio
async def test_mode_switch_keeps_identity_transcript_and_command_history(app):
    register(app, "alphabet")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        path, access = await create_alphabet_session(client)
        edit = await client.patch(
            f"{path}/transcript",
            headers=command(access),
            json={"expected_revision": 0, "items": [{"text": "مرحبا 123"}]},
        )
        assert edit.status_code == 200, edit.text
        original = edit.json()["session"]
        body = {"mode": "word", "expected_revision": 1, "expected_state_version": 0}
        switch = command(access)
        unavailable = await client.post(f"{path}/mode", headers=switch, json=body)
        error_code(unavailable, 503, "MODEL_UNAVAILABLE")
        before = (await client.get(path, headers=access)).json()["session"]
        assert before["mode"] == original["mode"]
        assert before["state_version"] == original["state_version"]
        assert before["transcript"] == original["transcript"]

        register(app, "word")
        changed = await client.post(f"{path}/mode", headers=switch, json=body)
        assert changed.status_code == 200, changed.text
        session = changed.json()["session"]
        assert session["mode"] == "word"
        assert session["model_version"] == "word-test-v1"
        assert session["session_id"] == original["session_id"]
        assert session["status"] == "paused"
        assert session["stream_id"] is None
        assert session["state_version"] == 1
        assert session["transcript"] == original["transcript"]
        assert (
            await client.post(f"{path}/mode", headers=switch, json=body)
        ).json() == changed.json()

        stale = await client.post(
            f"{path}/mode", headers=command(access), json={**body, "mode": "alphabet"}
        )
        error_code(stale, 409, "STATE_CONFLICT")
        conflict = await client.post(
            f"{path}/mode", headers=switch, json={**body, "mode": "alphabet"}
        )
        error_code(conflict, 409, "IDEMPOTENCY_CONFLICT")
        back = await client.post(
            f"{path}/mode",
            headers=command(access),
            json={**body, "mode": "alphabet", "expected_state_version": 1},
        )
        assert back.status_code == 200
        assert back.json()["session"]["transcript"] == original["transcript"]


@pytest.mark.asyncio
async def test_capture_start_requires_socket_and_current_state(app):
    register(app, "alphabet")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        path, access = await create_alphabet_session(client)
        body = {"action": "start", "expected_revision": 0, "expected_state_version": 0}
        missing_socket = await client.post(
            f"{path}/capture", headers=command(access), json=body
        )
        error_code(missing_socket, 409, "SOCKET_REQUIRED")
        no_command = await client.post(f"{path}/capture", headers=access, json=body)
        error_code(no_command, 422, "VALIDATION_ERROR")
        stale = await client.post(
            f"{path}/capture",
            headers=command(access),
            json={**body, "expected_revision": 1},
        )
        error_code(stale, 409, "REVISION_CONFLICT")


@pytest.mark.asyncio
async def test_end_review_delete_and_capability_bound_tombstone():
    now = [0.0]
    app = create_app(
        Settings(_env_file=None, idle_timeout_seconds=5, end_review_seconds=10),
        clock=Clock(lambda: now[0]),
        load_models=False,
    )
    register(app, "alphabet")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        path, access = await create_alphabet_session(client)
        edit = await client.patch(
            f"{path}/transcript",
            headers=command(access),
            json={"expected_revision": 0, "items": [{"text": "مرحبا"}]},
        )
        assert edit.status_code == 200
        now[0] = 4
        end_key = command(access)
        end = await client.post(
            f"{path}/end", headers=end_key, json={"expected_revision": 1}
        )
        assert end.status_code == 200
        assert end.json()["session"]["status"] == "ended"
        assert end.json()["session"]["transcript"]["revision"] == 1
        assert (
            await client.post(
                f"{path}/end", headers=end_key, json={"expected_revision": 1}
            )
        ).json() == end.json()
        new_end = await client.post(
            f"{path}/end", headers=command(access), json={"expected_revision": 1}
        )
        error_code(new_end, 409, "SESSION_ENDED")

        now[0] = 6
        read = await client.get(path, headers=access)
        assert read.status_code == 200
        assert read.json()["session"]["transcript"]["text"] == "مرحبا"
        export = await client.get(
            f"{path}/export?format=txt&revision=1", headers=access
        )
        assert export.status_code == 200 and export.text == "مرحبا"

        no_body = await client.request("DELETE", path, headers=access, json={})
        error_code(no_body, 422, "VALIDATION_ERROR")
        deleted = await client.delete(path, headers=access)
        assert deleted.status_code == 204 and deleted.content == b""
        assert (await client.delete(path, headers=access)).status_code == 204
        error_code(await client.get(path, headers=access), 410, "SESSION_DELETED")
        wrong = {"Authorization": "Bearer wrong"}
        error_code(await client.delete(path, headers=wrong), 404, "SESSION_NOT_FOUND")
        now[0] += 120
        error_code(await client.delete(path, headers=access), 404, "SESSION_NOT_FOUND")


@pytest.mark.asyncio
async def test_idle_reads_do_not_renew_and_expiry_releases_capacity():
    now = [0.0]
    app = create_app(
        Settings(_env_file=None, idle_timeout_seconds=5, max_sessions=1),
        clock=Clock(lambda: now[0]),
        load_models=False,
    )
    register(app, "alphabet")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        path, access = await create_alphabet_session(client)
        capped = await client.post("/api/v1/sessions", json={"mode": "alphabet"})
        error_code(capped, 429, "SESSION_LIMIT")
        assert capped.headers["retry-after"] == "15"
        now[0] = 4
        assert (await client.get(path, headers=access)).status_code == 200
        now[0] = 5
        error_code(await client.get(path, headers=access), 410, "SESSION_EXPIRED")
        error_code(await client.delete(path, headers=access), 410, "SESSION_EXPIRED")
        await create_alphabet_session(client)


def test_openapi_lists_actual_create_response(app):
    api = app.openapi()
    operation = api["paths"]["/api/v1/sessions"]["post"]
    responses = operation["responses"]
    assert responses["201"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/SessionCreatedResponse"
    )
    assert responses["503"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ErrorEnvelope"
    )
    assert api["components"]["securitySchemes"]["SessionToken"]["scheme"] == "bearer"
    assert api["paths"]["/api/v1/sessions/{session_id}"]["get"]["security"] == [
        {"SessionToken": []}
    ]


@pytest.mark.asyncio
async def test_delete_expiry_after_authentication_returns_gone(monkeypatch):
    now = [0.0]
    app = create_app(
        Settings(_env_file=None, idle_timeout_seconds=10),
        clock=Clock(lambda: now[0]),
        load_models=False,
    )
    register(app, "alphabet")
    store = app.state.session_store
    authenticate = store.authenticate

    def authenticate_before_deadline(session_id, token):
        record = authenticate(session_id, token)
        now[0] = 10
        return record

    monkeypatch.setattr(store, "authenticate", authenticate_before_deadline)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        path, access = await create_alphabet_session(client)
        now[0] = 9.9
        error_code(await client.delete(path, headers=access), 410, "SESSION_EXPIRED")
