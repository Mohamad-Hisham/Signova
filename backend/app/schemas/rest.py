"""Strict request bodies and response envelopes for the REST API."""

from typing import Annotated, Literal
from unicodedata import normalize

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
)

from app.schemas.common import ModelMode, Session


def normalize_rest_text(value: object) -> object:
    if isinstance(value, str):
        return normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n"))
    return value


NFCText = Annotated[
    str,
    BeforeValidator(normalize_rest_text),
    Field(min_length=1, max_length=2000),
]


class ConfiguredModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SessionCreateRequest(ConfiguredModel):
    mode: ModelMode
    recovery_enabled: StrictBool = False


class CaptureRequest(ConfiguredModel):
    expected_revision: StrictInt = Field(ge=0)
    expected_state_version: StrictInt = Field(ge=0)
    action: Literal["start", "pause"]


class ModeChangeRequest(ConfiguredModel):
    mode: ModelMode
    expected_revision: StrictInt = Field(ge=0)
    expected_state_version: StrictInt = Field(ge=0)


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


class SessionResponse(ConfiguredModel):
    session: Session


class SessionCreatedResponse(SessionResponse):
    session_token: str


class ConfirmResponse(SessionResponse):
    item_id: str
