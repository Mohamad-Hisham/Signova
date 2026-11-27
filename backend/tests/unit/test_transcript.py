from types import SimpleNamespace

import pytest

from app.services.commands import RevisionConflict
from app.services.transcript import (
    CaptureActiveError,
    InvalidTranscriptItem,
    SpaceNotAllowedError,
    TranscriptLimitExceeded,
    WrongModeError,
    append_model_item,
    append_space,
    clear_transcript,
    derive_text,
    public_transcript_items,
    replace_transcript,
    validate_transcript,
)


def transcript(mode="alphabet"):
    return SimpleNamespace(
        mode=mode, status="paused", items=[], transcript_revision=0, updated_at=None
    )


def add_model_item(record, text, kind):
    return append_model_item(
        record,
        text=text,
        kind=kind,
        label_id="TEST",
        score=0.97,
        model_version="test-v1",
    )


def test_homogeneous_spacing_and_normalization():
    assert derive_text("word", [{"text": "مرحبا"}, {"text": " "}, {"text": "بكم"}]) == (
        "مرحبا بكم"
    )
    assert derive_text("alphabet", [{"text": "ا"}, {"text": "\u0654"}]) == "أ"
    assert (
        derive_text("alphabet", [{"text": "أ"}, {"text": " "}, {"text": "ب"}]) == "أ ب"
    )


def test_mixed_transcript_preserves_spacing_when_active_mode_changes():
    record = transcript("word")
    add_model_item(record, "مرحبا", "word")
    add_model_item(record, "بكم", "word")
    record.mode = "alphabet"
    add_model_item(record, "أ", "letter")
    add_model_item(record, "ب", "letter")
    append_space(record, 4)
    record.mode = "word"
    add_model_item(record, "شكرا", "word")
    record.mode = "alphabet"
    add_model_item(record, "ج", "letter")

    assert derive_text("alphabet", record.items) == "مرحبا بكم أب شكرا ج"
    assert derive_text("word", record.items) == "مرحبا بكم أب شكرا ج"
    assert record.transcript_revision == 7


def test_replacement_preserves_provenance_and_rendering_for_unchanged_items():
    record = transcript("word")
    first = add_model_item(record, "مرحبا", "word")
    second = add_model_item(record, "بكم", "word")
    record.mode = "alphabet"
    replace_transcript(
        record,
        2,
        [
            {"item_id": first["item_id"], "text": first["text"]},
            {"item_id": second["item_id"], "text": "بك"},
            {"text": "ا\u0654\r\nب\rج\t"},
        ],
    )

    assert record.items[0] == first
    assert record.items[1]["item_id"] != second["item_id"]
    for item in record.items[1:]:
        assert item["kind"] == "manual"
        assert item["source"] == "user"
        assert item["confirmed_by"] == "edit"
        assert item["label_id"] is item["score"] is item["model_version"] is None
    assert derive_text("alphabet", record.items) == "مرحبا بك أ\nب\nج\t"
    assert derive_text("word", record.items) == "مرحبا بك أ\nب\nج\t"
    public = public_transcript_items(record.items)
    assert all("_render_mode" not in item for item in public)
    assert all(item["created_at"].endswith("Z") for item in public)
    assert record.transcript_revision == 3


@pytest.mark.parametrize(
    ("replacements", "bad_field"),
    [
        ([{"text": "أ"}, {"text": "ب\x00ج"}], "items.1.text"),
        ([{"text": "\ud800"}], "items.0.text"),
        ([{"text": ""}], "items.0.text"),
        ([{"text": "أ" * 2001}], "items.0.text"),
        ([{"item_id": "foreign-id", "text": "أ"}], "items.0.item_id"),
    ],
)
def test_invalid_item_cannot_partially_replace_transcript(replacements, bad_field):
    record = transcript()
    existing = add_model_item(record, "أ", "letter")

    with pytest.raises(InvalidTranscriptItem) as failure:
        replace_transcript(record, 1, replacements)

    assert failure.value.path == bad_field
    assert record.items == [existing]
    assert record.transcript_revision == 1


def test_duplicate_item_identity_cannot_partially_replace_transcript():
    record = transcript()
    existing = add_model_item(record, "أ", "letter")
    duplicate = {"item_id": existing["item_id"], "text": "ب"}

    with pytest.raises(InvalidTranscriptItem, match="Duplicate item ID"):
        replace_transcript(record, 1, [duplicate, duplicate])

    assert record.items == [existing]
    assert record.transcript_revision == 1


def test_transcript_limits_count_items_and_rendered_characters():
    items = [{"kind": "word", "text": "أ"}, {"kind": "letter", "text": "ب"}]
    validate_transcript("word", items, max_items=2, max_characters=3)
    with pytest.raises(TranscriptLimitExceeded):
        validate_transcript("word", items, max_items=1)
    with pytest.raises(TranscriptLimitExceeded):
        validate_transcript("word", items, max_characters=2)


def test_append_and_replace_reject_limits_without_mutating_record():
    record = transcript()
    replace_transcript(record, 0, [{"text": "أ" * 2000}] * 10)
    previous_items = record.items
    previous_time = record.updated_at

    with pytest.raises(TranscriptLimitExceeded):
        add_model_item(record, "ب", "letter")
    with pytest.raises(TranscriptLimitExceeded):
        replace_transcript(record, 1, [{"text": "أ" * 2000}] * 11)

    assert record.items is previous_items
    assert record.updated_at is previous_time
    assert record.transcript_revision == 1


def test_space_and_clear_enforce_state_revision_and_idempotent_order():
    record = transcript()
    with pytest.raises(SpaceNotAllowedError, match="Leading"):
        append_space(record, 0)
    add_model_item(record, "أ", "letter")
    with pytest.raises(RevisionConflict):
        append_space(record, 0)
    record.mode = "word"
    with pytest.raises(WrongModeError):
        append_space(record, 1)
    record.mode = "alphabet"
    record.status = "capturing"
    with pytest.raises(CaptureActiveError):
        append_space(record, 1)
    with pytest.raises(CaptureActiveError):
        replace_transcript(record, 1, [])
    record.status = "paused"
    append_space(record, 1)
    with pytest.raises(SpaceNotAllowedError, match="Repeated"):
        append_space(record, 2)
    with pytest.raises(RevisionConflict):
        clear_transcript(record, 1)
    clear_transcript(record, 2)
    assert record.items == []
    assert record.transcript_revision == 3
