# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve strict REST creation, capture, confirm, space, replacement, clear and end
#   input schemas.
# Owner: Hisham.
# Expected inputs: Untrusted documented request bodies/query/header identities.
# Expected outputs: Future validated operation inputs or safe field-path validation errors.
# Responsibilities: Forbid unknown fields, enforce nonboolean integers, UUID command headers,
#   text/code-point and body limits.
# Connections: api handlers, common.py and commands/transcript services.
# Future implementation: Define Pydantic v2 request contracts with exact v1 field names.
# Rules and limitations: Do not accept client score/source/label provenance, guessed revisions,
#   mode changes or empty bodies on no-body routes.
# Expected tests or acceptance: Missing/extra fields, duplicate/foreign IDs and malformed
#   revisions return safe 422 before mutation; valid stale revisions use 409.


from typing import Annotated, Literal
from unicodedata import normalize

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictInt,
)

NFCText = Annotated[
    str,
    BeforeValidator(lambda value: normalize("NFC", value)),
    Field(min_length=1, max_length=2000),
]


class ConfiguredModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SessionCreateRequest(ConfiguredModel):
    mode: Literal["alphabet", "word"]
    recovery_enabled: bool = False


class CaptureRequest(ConfiguredModel):
    expected_revision: StrictInt = Field(ge=0)
    expected_state_version: StrictInt = Field(ge=0)
    action: Literal["start", "pause"]


class ConfirmRequest(ConfiguredModel):
    expected_revision: StrictInt = Field(ge=0)
    candidate_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)


class SpaceRequest(ConfiguredModel):
    expected_revision: StrictInt = Field(ge=0)


class TranscriptReplacementItem(ConfiguredModel):
    item_id: str | None = None
    text: NFCText


class TranscriptReplaceRequest(ConfiguredModel):
    expected_revision: StrictInt = Field(ge=0)
    items: list[TranscriptReplacementItem] = Field(
        max_length=2000,
    )


class TranscriptClearRequest(ConfiguredModel):
    expected_revision: StrictInt = Field(ge=0)


class EndRequest(ConfiguredModel):
    expected_revision: StrictInt = Field(ge=0)


class VocabularyQuery(ConfiguredModel):
    mode: Literal["alphabet", "word"]


class ExportQuery(ConfiguredModel):
    format: Literal["txt"]
    revision: StrictInt = Field(ge=0)
