# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve canonical Session, Transcript, Item, Candidate and safe Error response
#   shapes.
# Owner: Ali.
# Expected inputs: Shared documented response fields and owner-approved semantics.
# Expected outputs: Future Pydantic v2 response objects with finite values and correct
#   nullability.
# Responsibilities: Separate transcript revision/state_version, preserve Unicode and provenance,
#   forbid sensitive diagnostics.
# Connections: rest.py, events.py, API/WS serializers and services.
# Future implementation: Define exact handbook fields after remaining deadline/score decisions
#   are closed.
# Rules and limitations: No extra English keys, model tensors, tokens in snapshots or private
#   text in errors.
# Expected tests or acceptance: Canonical snapshots validate; nonfinite scores/invalid modes
#   fail; item/candidate distinction and null edited metadata preserved.


import math
import unicodedata
from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictInt,
)
from pydantic.types import StringConstraints
from pydantic_core import PydanticCustomError

ModelMode = Literal["alphabet", "word"]
SessionStatus = Literal["paused", "capturing", "disconnected", "ended"]
ItemKind = Literal["word", "letter", "space", "manual"]
ItemSource = Literal["model", "user"]
ConfirmationType = Literal["auto", "manual", "edit"]


def validate_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must include a UTC timezone")

    if value.utcoffset().total_seconds() != 0:
        raise ValueError("datetime must use UTC")

    return value.astimezone(UTC)


def validate_score(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PydanticCustomError("score_type", "score must be a number")

    score = float(value)

    if not math.isfinite(score):
        raise ValueError("score must be finite")

    if score < 0 or score > 1:
        raise ValueError("score must be between 0 and 1")

    return score


def normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


UTCDateTime = Annotated[datetime, AfterValidator(validate_utc_datetime)]
Score = Annotated[
    float,
    BeforeValidator(validate_score),
    Field(ge=0, le=1),
]
PublicText = Annotated[
    str,
    StringConstraints(min_length=1, max_length=2000),
]


class Item(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    text: Annotated[
        str,
        BeforeValidator(normalize_text),
        StringConstraints(min_length=1, max_length=2000),
    ]
    kind: ItemKind
    source: ItemSource
    label_id: str | None
    score: Score | None
    model_version: str | None
    confirmed_by: ConfirmationType
    created_at: UTCDateTime

class Transcript(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revision: StrictInt = Field(ge=0)
    items: list[Item] = Field(max_length=2000)
    text: Annotated[
        str,
        BeforeValidator(normalize_text),
    ]
    updated_at: UTCDateTime

class Candidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    stream_id: str
    mode: ModelMode
    label_id: str
    text: Annotated[
        str,
        BeforeValidator(normalize_text),
        StringConstraints(min_length=1, max_length=2000),
    ]
    score: Score
    stable: bool
    eligible: bool
    expires_in_ms: StrictInt = Field(ge=0)
    model_version: str

class Session(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    mode: ModelMode
    status: SessionStatus
    state_version: StrictInt = Field(ge=0)
    expires_at: UTCDateTime
    absolute_expires_at: UTCDateTime
    idle_timeout_seconds: StrictInt = Field(gt=0)
    reconnect_grace_seconds: StrictInt = Field(gt=0)
    model_version: str
    stream_id: str | None
    recovery_enabled: bool
    transcript: Transcript

class ErrorDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    retryable: bool
    details: dict[str, object] = Field(default_factory=dict)


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: ErrorDetails
    request_id: str