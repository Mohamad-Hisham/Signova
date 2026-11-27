from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app
from app.services.transcript import append_model_item


class RecognitionAdapterStub:
    model_version = "test-v1"
    confirmation_policy = "manual"
    required_sample_fps = None
    window_samples = 1
    labels = ()

    def __init__(self, mode):
        self.mode = mode

    def reset_stream(self, stream_id):
        pass

    def predict(self, frames, times_ms):
        raise AssertionError("Transcript routes must not run inference")


@pytest.fixture
def transcript_app():
    app = create_app(Settings(environment="test"), load_models=False)
    for mode in ("alphabet", "word"):
        app.state.adapter_registry.register(mode, RecognitionAdapterStub(mode))
    return app


async def new_session(client, mode="alphabet", *, recovery_enabled=False):
    response = await client.post(
        "/api/v1/sessions",
        json={"mode": mode, "recovery_enabled": recovery_enabled},
    )
    assert response.status_code == 201
    payload = response.json()
    session_id = payload["session"]["session_id"]
    authorization = {"Authorization": f"Bearer {payload['session_token']}"}
    return f"/api/v1/sessions/{session_id}", authorization


def command(authorization, *, key=None):
    return {**authorization, "Idempotency-Key": str(key or uuid4())}


def assert_error(response, status, code):
    assert response.status_code == status, response.text
    assert response.json()["error"]["code"] == code


@pytest.mark.asyncio
async def test_export_empty_replaced_stale_and_ended_transcript(transcript_app):
    async with AsyncClient(
        transport=ASGITransport(app=transcript_app), base_url="http://test"
    ) as client:
        path, authorization = await new_session(client)
        record = transcript_app.state.session_store.authenticate(
            path.rsplit("/", 1)[1], authorization["Authorization"].split(" ")[1]
        )
        empty = await client.get(
            path + "/export?format=txt&revision=0", headers=authorization
        )
        assert empty.status_code == 204
        assert empty.content == b""
        assert empty.headers["x-transcript-revision"] == "0"
        assert empty.headers["cache-control"] == "no-store"

        replacement_text = "ا\u0654هلاً\r\nב\t2026"
        replaced = await client.patch(
            path + "/transcript",
            headers=command(authorization),
            json={"expected_revision": 0, "items": [{"text": replacement_text}]},
        )
        assert replaced.status_code == 200, replaced.text
        expected_text = "أهلاً\nב\t2026"
        transcript = replaced.json()["session"]["transcript"]
        assert transcript["text"] == expected_text
        assert transcript["items"][0]["created_at"].endswith("Z")
        assert transcript["revision"] == 1
        assert "_render_mode" not in transcript["items"][0]
        assert replaced.headers["cache-control"] == "no-store"

        idle = record.idle_deadline
        exported = await client.get(
            path + "/export?format=txt&revision=1", headers=authorization
        )
        assert exported.status_code == 200, exported.text
        assert exported.content == expected_text.encode("utf-8")
        assert exported.headers["content-type"] == "text/plain; charset=utf-8"
        assert exported.headers["content-disposition"] == (
            'attachment; filename="signova-transcript.txt"'
        )
        assert exported.headers["cache-control"] == "no-store"
        assert exported.headers["x-transcript-revision"] == "1"
        assert record.idle_deadline == idle
        assert record.transcript_revision == 1
        assert record.status == "paused"

        stale = await client.get(
            path + "/export?format=txt&revision=0", headers=authorization
        )
        assert_error(stale, 409, "REVISION_CONFLICT")
        assert stale.json()["error"]["details"] == {"current_revision": 1}

        ended = await client.post(
            path + "/end",
            headers=command(authorization),
            json={"expected_revision": 1},
        )
        assert ended.status_code == 200, ended.text
        ended_export = await client.get(
            path + "/export?format=txt&revision=1", headers=authorization
        )
        assert ended_export.content == exported.content
        rejected = await client.post(
            path + "/transcript/clear",
            headers=command(authorization),
            json={"expected_revision": 1},
        )
        assert_error(rejected, 409, "SESSION_ENDED")


@pytest.mark.asyncio
async def test_export_rejects_invalid_query_and_unauthorized_access(transcript_app):
    async with AsyncClient(
        transport=ASGITransport(app=transcript_app), base_url="http://test"
    ) as client:
        path, authorization = await new_session(client)
        for query in (
            "revision=0",
            "format=txt",
            "format=pdf&revision=0",
            "format=txt&revision=-1",
            "format=txt&revision=0.0",
            "format=txt&revision=true",
            "format=txt&revision=0&other=1",
        ):
            rejected = await client.get(
                path + "/export?" + query, headers=authorization
            )
            assert_error(rejected, 422, "VALIDATION_ERROR")

        url = path + "/export?format=txt&revision=0"
        missing = await client.get(url)
        assert_error(missing, 401, "CREDENTIAL_REQUIRED")
        wrong = await client.get(url, headers={"Authorization": "Bearer wrong"})
        assert_error(wrong, 404, "SESSION_NOT_FOUND")
        bad_body = await client.request("GET", url, json={}, headers=authorization)
        assert_error(bad_body, 422, "VALIDATION_ERROR")


@pytest.mark.asyncio
async def test_replace_is_atomic_and_error_details_exclude_values(transcript_app):
    async with AsyncClient(
        transport=ASGITransport(app=transcript_app), base_url="http://test"
    ) as client:
        path, authorization = await new_session(client)
        url = path + "/transcript"
        for items in (
            [{"text": "candidate"}, {"text": "private\x00transcript"}],
            [{"text": 123}],
            [{"text": ""}],
            [{"text": "أ", "score": 1}],
            [{"text": "أ", "item_id": "private-foreign-id"}],
        ):
            rejected = await client.patch(
                url,
                headers=command(authorization),
                json={"expected_revision": 0, "items": items},
            )
            assert_error(rejected, 422, "VALIDATION_ERROR")
            assert "candidate" not in rejected.text
            assert "private" not in rejected.text

        overflowing = await client.patch(
            url,
            headers=command(authorization),
            json={
                "expected_revision": 0,
                "items": [{"text": "أ" * 2000}] * 11,
            },
        )
        assert_error(overflowing, 409, "TRANSCRIPT_LIMIT")
        assert (await client.get(path, headers=authorization)).json()["session"][
            "transcript"
        ]["revision"] == 0


@pytest.mark.asyncio
async def test_space_policy_and_shared_idempotency(transcript_app):
    async with AsyncClient(
        transport=ASGITransport(app=transcript_app), base_url="http://test"
    ) as client:
        path, authorization = await new_session(client)
        space = path + "/space"
        leading = await client.post(
            space, headers=command(authorization), json={"expected_revision": 0}
        )
        assert_error(leading, 409, "SPACE_NOT_ALLOWED")

        edit_headers = command(authorization)
        edit = await client.patch(
            path + "/transcript",
            headers=edit_headers,
            json={"expected_revision": 0, "items": [{"text": "أ"}]},
        )
        assert edit.status_code == 200, edit.text
        reused_key = await client.post(
            space, headers=edit_headers, json={"expected_revision": 1}
        )
        assert_error(reused_key, 409, "IDEMPOTENCY_CONFLICT")

        space_headers = command(authorization)
        first = await client.post(
            space, headers=space_headers, json={"expected_revision": 1}
        )
        assert first.status_code == 200, first.text
        result = first.json()["session"]["transcript"]
        assert result["text"] == "أ "
        assert result["revision"] == 2
        item = result["items"][-1]
        assert item["kind"] == "space"
        assert item["source"] == "user"
        assert item["confirmed_by"] == "manual"
        assert item["label_id"] is item["score"] is item["model_version"] is None

        replay = await client.post(
            space, headers=space_headers, json={"expected_revision": 1}
        )
        assert replay.json() == first.json()
        repeated = await client.post(
            space, headers=command(authorization), json={"expected_revision": 2}
        )
        assert_error(repeated, 409, "SPACE_NOT_ALLOWED")
        no_key = await client.post(
            space, headers=authorization, json={"expected_revision": 2}
        )
        assert_error(no_key, 422, "VALIDATION_ERROR")

        word_path, word_auth = await new_session(client, "word")
        wrong_mode = await client.post(
            word_path + "/space",
            headers=command(word_auth),
            json={"expected_revision": 0},
        )
        assert_error(wrong_mode, 409, "WRONG_MODE")


@pytest.mark.asyncio
async def test_active_clear_invalidates_stream_discards_pending_and_replays_once(
    transcript_app,
):
    publish = Mock(wraps=transcript_app.state.live.publish)
    invalidate = Mock(wraps=transcript_app.state.recognition_service.invalidate_stream)
    with (
        patch.object(transcript_app.state.live, "publish", publish),
        patch.object(
            transcript_app.state.recognition_service, "invalidate_stream", invalidate
        ),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=transcript_app), base_url="http://test"
        ) as client:
            path, authorization = await new_session(client, recovery_enabled=True)
            edit_headers = command(authorization)
            body = {"expected_revision": 0, "items": [{"text": "أ"}]}
            saved = await client.patch(
                path + "/transcript", headers=edit_headers, json=body
            )
            assert saved.status_code == 200, saved.text
            record = transcript_app.state.session_store.authenticate(
                path.rsplit("/", 1)[1], authorization["Authorization"].split(" ")[1]
            )
            record.status = "capturing"
            record.stream_id = "active-stream"
            record.state_version = 1
            capture_edit = await client.patch(
                path + "/transcript",
                headers=command(authorization),
                json={"expected_revision": 1, "items": []},
            )
            assert_error(capture_edit, 409, "CAPTURE_ACTIVE")
            publish.reset_mock()

            clear_headers = command(authorization)
            url = path + "/transcript/clear"
            cleared = await client.post(
                url, headers=clear_headers, json={"expected_revision": 1}
            )
            replay = await client.post(
                url, headers=clear_headers, json={"expected_revision": 1}
            )
            old_edit = await client.patch(
                path + "/transcript", headers=edit_headers, json=body
            )
            assert_error(old_edit, 409, "REVISION_CONFLICT")

    assert cleared.status_code == 200, cleared.text
    assert replay.json() == cleared.json()
    snapshot = cleared.json()["session"]
    assert snapshot["status"] == "paused"
    assert snapshot["state_version"] == 2
    assert snapshot["stream_id"] is None
    assert snapshot["recovery_enabled"] is False
    assert snapshot["transcript"]["revision"] == 2
    assert snapshot["transcript"]["items"] == []
    assert snapshot["transcript"]["text"] == ""
    invalidate.assert_called_once_with("active-stream")
    assert [call.args[1] for call in publish.call_args_list] == [
        "transcript.updated",
        "session.state",
    ]
    assert publish.call_args_list[0].kwargs["discard_pending"] is True


@pytest.mark.asyncio
async def test_mixed_export_keeps_items_when_switching_modes(transcript_app):
    async with AsyncClient(
        transport=ASGITransport(app=transcript_app), base_url="http://test"
    ) as client:
        path, authorization = await new_session(client)
        record = transcript_app.state.session_store.authenticate(
            path.rsplit("/", 1)[1], authorization["Authorization"].split(" ")[1]
        )
        append_model_item(
            record,
            text="أ",
            kind="letter",
            label_id="ALEF",
            score=0.9,
            model_version="test-v1",
        )
        initial = await client.get(path, headers=authorization)
        switched = await client.post(
            path + "/mode",
            headers=command(authorization),
            json={"mode": "word", "expected_revision": 1, "expected_state_version": 0},
        )
        assert switched.status_code == 200, switched.text
        assert (
            switched.json()["session"]["transcript"]
            == initial.json()["session"]["transcript"]
        )
        append_model_item(
            record,
            text="مرحبا",
            kind="word",
            label_id="HELLO",
            score=0.9,
            model_version="test-v1",
        )
        mixed = await client.get(
            path + "/export?format=txt&revision=2", headers=authorization
        )
        assert mixed.text == "أ مرحبا"
        returned = await client.post(
            path + "/mode",
            headers=command(authorization),
            json={
                "mode": "alphabet",
                "expected_revision": 2,
                "expected_state_version": 1,
            },
        )
        assert returned.status_code == 200, returned.text
        returned_session = returned.json()["session"]
        assert returned_session["mode"] == "alphabet"
        assert returned_session["transcript"]["text"] == mixed.text
        assert returned_session["transcript"]["revision"] == 2
