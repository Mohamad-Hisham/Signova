import pytest
from pydantic import ValidationError

from app.schemas.rest import (
    CaptureRequest,
    ConfirmRequest,
    EndRequest,
    ExportQuery,
    SessionCreateRequest,
    SpaceRequest,
    TranscriptClearRequest,
    TranscriptReplacementItem,
    TranscriptReplaceRequest,
    VocabularyQuery,
)


def test_valid_session_creation():
    result = SessionCreateRequest(
        mode="word",
        recovery_enabled=False,
    )

    assert result.mode == "word"
    assert result.recovery_enabled is False


def test_invalid_session_mode():
    # "speech" is not a public recognition mode. Only alphabet and word are allowed.
    with pytest.raises(ValidationError):
        SessionCreateRequest(mode="speech")


def test_unknown_session_field():
    # Model scores are server-owned; an unknown score field must be rejected.
    with pytest.raises(ValidationError):
        SessionCreateRequest(mode="word", score=0.99)


def test_valid_capture_requests():
    start = CaptureRequest(
        expected_revision=0,
        expected_state_version=1,
        action="start",
    )
    pause = CaptureRequest(
        expected_revision=0,
        expected_state_version=2,
        action="pause",
    )

    assert start.action == "start"
    assert pause.action == "pause"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("expected_revision", True),
        ("expected_revision", "1"),
        ("expected_revision", -1),
        ("expected_state_version", True),
        ("expected_state_version", "1"),
        ("action", "resume"),
    ],
)
def test_invalid_capture_values(field, value):
    # True and string values are not strict integers.
    # Negative revisions are invalid, and resume is not a public capture action.
    data = {
        "expected_revision": 0,
        "expected_state_version": 1,
        "action": "start",
    }
    data[field] = value

    with pytest.raises(ValidationError):
        CaptureRequest(**data)


def test_unknown_capture_field():
    # Candidate state and text cannot be supplied in a capture request.
    with pytest.raises(ValidationError):
        CaptureRequest(
            expected_revision=0,
            expected_state_version=1,
            action="start",
            candidate_id="candidate-1",
        )


def test_valid_confirm_request():
    result = ConfirmRequest(
        expected_revision=2,
        candidate_id="candidate-1",
        stream_id="stream-1",
    )

    assert result.candidate_id == "candidate-1"
    assert result.stream_id == "stream-1"


@pytest.mark.parametrize(
    "data",
    [
        {
            "expected_revision": 2,
            "candidate_id": "",
            "stream_id": "stream-1",
        },
        {
            "expected_revision": True,
            "candidate_id": "candidate-1",
            "stream_id": "stream-1",
        },
        {
            "expected_revision": "2",
            "candidate_id": "candidate-1",
            "stream_id": "stream-1",
        },
        {
            "expected_revision": 2,
            "candidate_id": "candidate-1",
            "stream_id": "",
        },
    ],
)
def test_invalid_confirm_request(data):
    # Empty candidate/stream IDs are invalid.
    # A boolean or string revision is not a strict integer.
    with pytest.raises(ValidationError):
        ConfirmRequest(**data)


def test_confirm_rejects_browser_owned_evidence():
    # The browser identifies evidence. It cannot supply text, label or score.
    with pytest.raises(ValidationError):
        ConfirmRequest(
            expected_revision=2,
            candidate_id="candidate-1",
            stream_id="stream-1",
            text="ماء",
            score=0.94,
        )


def test_valid_transcript_replacement():
    result = TranscriptReplaceRequest(
        expected_revision=3,
        items=[
            TranscriptReplacementItem(item_id="item-1", text="ماء"),
            TranscriptReplacementItem(text="مرحبا"),
        ],
    )

    assert result.items[0].text == "ماء"
    assert result.items[1].item_id is None


def test_empty_transcript_replacement_is_valid():
    # An empty list is a valid full replacement that clears all transcript items.
    result = TranscriptReplaceRequest(expected_revision=3, items=[])
    assert result.items == []


@pytest.mark.parametrize(
    "text",
    [
        "",
        "أ" * 2001,
    ],
)
def test_invalid_transcript_item_text(text):
    # Item text must contain 1 to 2000 Unicode code points.
    with pytest.raises(ValidationError):
        TranscriptReplacementItem(text=text)


def test_transcript_item_rejects_provenance_fields():
    # Provenance fields are server-owned and must not come from the browser.
    with pytest.raises(ValidationError):
        TranscriptReplacementItem(
            text="ماء",
            source="model",
            score=0.94,
            label_id="WORD_WATER",
        )


@pytest.mark.parametrize("revision", [True, "3", -1])
def test_invalid_transcript_replacement_revision(revision):
    # Revision must be a real, nonnegative integer.
    with pytest.raises(ValidationError):
        TranscriptReplaceRequest(expected_revision=revision, items=[])


def test_transcript_replacement_rejects_too_many_items():
    # The initial contract allows at most 2000 items.
    items = [TranscriptReplacementItem(text="ماء")] * 2001

    with pytest.raises(ValidationError):
        TranscriptReplaceRequest(expected_revision=3, items=items)


def test_small_mutation_requests():
    assert SpaceRequest(expected_revision=3).expected_revision == 3
    assert TranscriptClearRequest(expected_revision=3).expected_revision == 3
    assert EndRequest(expected_revision=3).expected_revision == 3


@pytest.mark.parametrize(
    "value",
    [True, "3", -1],
)
def test_small_mutation_requests_reject_invalid_revision(value):
    # Clear, space and end use the same strict transcript revision rule.
    for request_type in (SpaceRequest, TranscriptClearRequest, EndRequest):
        with pytest.raises(ValidationError):
            request_type(expected_revision=value)


def test_valid_query_schemas():
    assert VocabularyQuery(mode="word").mode == "word"
    assert ExportQuery(format="txt", revision=3).revision == 3


@pytest.mark.parametrize(
    "request_type,data",
    [
        (VocabularyQuery, {"mode": "speech"}),
        (ExportQuery, {"format": "csv", "revision": 3}),
        (ExportQuery, {"format": "txt", "revision": True}),
        (ExportQuery, {"format": "txt", "revision": "3"}),
    ],
)
def test_invalid_query_schemas(request_type, data):
    # Vocabulary is limited to public modes.
    # Export is limited to txt and requires a strict integer revision.
    with pytest.raises(ValidationError):
        request_type(**data)
