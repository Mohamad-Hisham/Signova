# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve authoritative temporary confirmed transcript validation and atomic snapshots.
# Owner: Ali.
# Expected inputs: Confirmed current recognition items, expected revisions, full edit lists,
#   explicit space and clear intents.
# Expected outputs: Future canonical items/derived text/revision snapshots and committed item
#   identity.
# Responsibilities: Validate all before mutation, consume segment once, preserve unchanged
#   metadata, clear changed provenance, enforce limits and purge old content-bearing replies on
#   Clear.
# Connections: Session lock, commands.py, recognition/word gate, API/WS serializers and time/ID
#   utilities.
# Future implementation: Implement append/replacement/space/clear authority in RAM with no
#   partial updates.
# Rules and limitations: Candidates never append directly; no duplicate commit, stale revision
#   overwrite, server history, grammar rewrite or correction-to-training feed.
# Expected tests or acceptance: Revision increments once per mutation; parallel confirms once;
#   Arabic joining/NFC/code points correct; late result or cached old response cannot resurrect
#   cleared text.

import unicodedata

from app.utilities.ids import new_uuid
from app.utilities.time import utc_now


class TranscriptLimitExceeded(Exception):
    pass


class RevisionConflict(Exception):
    pass


class CaptureActiveError(Exception):
    pass


class WrongModeError(Exception):
    pass


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def derive_text(mode: str, items: list[dict]) -> str:
    if mode == "word":
        words = [
            item["text"] for item in items if item["text"] and item["text"].strip()
        ]
        return " ".join(words)
    return "".join(item["text"] for item in items)


def validate_transcript(
    mode: str,
    items: list[dict],
    *,
    max_items: int = 2000,
    max_characters: int = 20_000,
) -> None:
    if len(items) > max_items:
        raise TranscriptLimitExceeded
    if len(derive_text(mode, items)) > max_characters:
        raise TranscriptLimitExceeded


def append_model_item(
    record,
    *,
    text: str,
    kind: str,
    label_id: str,
    score: float,
    model_version: str,
    confirmed_by: str = "manual",
) -> dict:
    item = {
        "item_id": new_uuid(),
        "text": normalize_text(text),
        "kind": kind,
        "source": "model",
        "label_id": label_id,
        "score": score,
        "model_version": model_version,
        "confirmed_by": confirmed_by,
        "created_at": utc_now(),
    }
    candidates = [*record.items, item]
    validate_transcript(record.mode, candidates)
    record.items = candidates
    record.transcript_revision += 1
    record.updated_at = utc_now()
    return item


def append_space(record, expected_revision: int) -> None:
    if record.mode != "alphabet":
        raise WrongModeError
    if record.status == "capturing":
        raise CaptureActiveError
    if record.transcript_revision != expected_revision:
        raise RevisionConflict
    if not record.items:
        raise ValueError("Leading space is not allowed")
    if record.items[-1]["kind"] == "space":
        raise ValueError("Repeated space is not allowed")

    item = {
        "item_id": new_uuid(),
        "text": " ",
        "kind": "space",
        "source": "user",
        "label_id": None,
        "score": None,
        "model_version": None,
        "confirmed_by": "manual",
        "created_at": utc_now(),
    }
    candidates = [*record.items, item]
    validate_transcript(record.mode, candidates)
    record.items = candidates
    record.transcript_revision += 1
    record.updated_at = utc_now()


def replace_transcript(
    record,
    expected_revision: int,
    replacements: list[dict],
) -> None:
    if record.status == "capturing":
        raise CaptureActiveError
    if record.transcript_revision != expected_revision:
        raise RevisionConflict

    existing_by_id = {item["item_id"]: item for item in record.items}
    seen_ids: set[str] = set()
    items: list[dict] = []

    for replacement in replacements:
        item_id = replacement.get("item_id")
        text = normalize_text(replacement["text"])
        if not 1 <= len(text) <= 2000:
            raise ValueError("Item text must contain 1 to 2000 code points")

        if item_id is not None:
            if item_id in seen_ids:
                raise ValueError("Duplicate item ID")
            if item_id not in existing_by_id:
                raise ValueError("Unknown item ID")
            seen_ids.add(item_id)
            existing = existing_by_id[item_id]
            if existing["text"] == text:
                items.append(existing.copy())
                continue

        items.append(
            {
                "item_id": new_uuid(),
                "text": text,
                "kind": "manual",
                "source": "user",
                "label_id": None,
                "score": None,
                "model_version": None,
                "confirmed_by": "edit",
                "created_at": utc_now(),
            }
        )

    validate_transcript(record.mode, items)
    record.items = items
    record.transcript_revision += 1
    record.updated_at = utc_now()


def clear_transcript(record, expected_revision: int) -> None:
    if record.transcript_revision != expected_revision:
        raise RevisionConflict
    record.items = []
    record.transcript_revision += 1
    record.updated_at = utc_now()
