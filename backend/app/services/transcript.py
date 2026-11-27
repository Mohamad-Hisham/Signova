"""Derive and mutate the confirmed transcript while the session lock is held."""

import unicodedata
from datetime import datetime

from app.services.commands import check_revision
from app.utilities.ids import new_uuid
from app.utilities.time import utc_now

MAX_TRANSCRIPT_ITEMS = 2000
MAX_TRANSCRIPT_CHARACTERS = 20_000
MAX_ITEM_CHARACTERS = 2000


class TranscriptLimitExceeded(Exception):
    pass


class CaptureActiveError(Exception):
    pass


class WrongModeError(Exception):
    pass


class SpaceNotAllowedError(ValueError):
    pass


class InvalidTranscriptItem(ValueError):
    def __init__(self, index: int, field: str, reason: str) -> None:
        super().__init__(reason)
        self.path = f"items.{index}.{field}"


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", text)


def _render_mode(item: dict, default: str) -> str:
    kind = item.get("kind")
    if kind == "word":
        return "word"
    if kind in ("letter", "space"):
        return "alphabet"
    return item.get("_render_mode", default)


def derive_text(mode: str, items: list[dict]) -> str:
    fragments: list[str] = []
    previous_mode = None
    for item in items:
        text = item["text"]
        item_mode = _render_mode(item, mode)
        if not text or (item_mode == "word" and not text.strip()):
            continue
        if previous_mode == item_mode == "word" or (
            fragments
            and previous_mode != item_mode
            and not fragments[-1][-1].isspace()
            and not text[0].isspace()
        ):
            fragments.append(" ")
        fragments.append(text)
        previous_mode = item_mode
    return normalize_text("".join(fragments))


def public_transcript_items(items: list[dict]) -> list[dict]:
    wire_items = []
    for item in items:
        wire_item = {key: value for key, value in item.items() if key != "_render_mode"}
        if isinstance(created_at := wire_item["created_at"], datetime):
            wire_item["created_at"] = created_at.isoformat().replace("+00:00", "Z")
        wire_items.append(wire_item)
    return wire_items


def validate_transcript(
    mode: str,
    items: list[dict],
    *,
    max_items: int = MAX_TRANSCRIPT_ITEMS,
    max_characters: int = MAX_TRANSCRIPT_CHARACTERS,
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
    check_revision(record, expected_revision)
    if record.mode != "alphabet":
        raise WrongModeError
    if record.status == "capturing":
        raise CaptureActiveError
    text = derive_text(record.mode, record.items)
    if not text:
        raise SpaceNotAllowedError("Leading space is not allowed.")
    if text.endswith(" "):
        raise SpaceNotAllowedError("Repeated space is not allowed.")

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
    check_revision(record, expected_revision)
    if record.status == "capturing":
        raise CaptureActiveError

    existing_by_id = {item["item_id"]: item for item in record.items}
    seen_ids: set[str] = set()
    items: list[dict] = []

    for index, replacement in enumerate(replacements):
        item_id = replacement.get("item_id")
        text = normalize_text(replacement["text"])
        if not 1 <= len(text) <= MAX_ITEM_CHARACTERS:
            raise InvalidTranscriptItem(
                index, "text", "Expected 1 to 2000 code points."
            )
        if any(
            unicodedata.category(character) in ("Cc", "Cs") and character not in "\t\n"
            for character in text
        ):
            raise InvalidTranscriptItem(index, "text", "Contains an invalid character.")

        render_mode = record.mode
        if item_id is not None:
            if item_id in seen_ids:
                raise InvalidTranscriptItem(index, "item_id", "Duplicate item ID.")
            if item_id not in existing_by_id:
                raise InvalidTranscriptItem(index, "item_id", "Unknown item ID.")
            seen_ids.add(item_id)
            existing = existing_by_id[item_id]
            if existing["text"] == text:
                items.append(existing.copy())
                continue
            render_mode = _render_mode(existing, record.mode)

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
                "_render_mode": render_mode,
            }
        )

    validate_transcript(record.mode, items)
    record.items = items
    record.transcript_revision += 1
    record.updated_at = utc_now()


def clear_transcript(record, expected_revision: int) -> None:
    check_revision(record, expected_revision)
    record.items = []
    record.transcript_revision += 1
    record.updated_at = utc_now()
