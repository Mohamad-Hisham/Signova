# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve all protocol v1 client messages, server envelopes and event data objects.
# Owner: Ali.
# Expected inputs: Untrusted auth/frame/ping objects and validated service notifications.
# Expected outputs: Future exact v1 parsed inputs/serialized envelopes.
# Responsibilities: Validate version/type, event/session identity, finite timing/scores and
#   message-specific data for every documented type.
# Connections: ws/live.py, common.py, recognition/session/transcript services and frontend
#   validators.
# Future implementation: Define strict protocol schemas and listed reason enumerations after
#   owner review.
# Rules and limitations: No binary v1, invented finish_clip/confirm message, token query or
#   unsupported extra fields.
# Expected tests or acceptance: Three client and eleven server types match docs;
#   wrong-version/unknown-field/nonfinite/oversized inputs fail safely.

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
)

from app.schemas.common import UTCDateTime


class ConfiguredWebSocketModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AuthMessage(ConfiguredWebSocketModel):
    protocol_version: Literal[1]
    type: Literal["auth"]
    session_token: str = Field(min_length=1)
    last_event_seq: StrictInt | None = Field(default=None, ge=0)


class FrameMessage(ConfiguredWebSocketModel):
    protocol_version: Literal[1]
    type: Literal["frame"]
    stream_id: str = Field(min_length=1)
    frame_seq: StrictInt = Field(ge=1)
    capture_ms: float = Field(ge=0)
    width: StrictInt = Field(gt=0, le=640)
    height: StrictInt = Field(gt=0, le=480)
    mirrored: Literal[False]
    image_b64: str = Field(min_length=1, max_length=218_454)


class PingMessage(ConfiguredWebSocketModel):
    protocol_version: Literal[1]
    type: Literal["ping"]
    nonce: str = Field(min_length=1, max_length=64)


class ServerEnvelope(ConfiguredWebSocketModel):
    protocol_version: Literal[1]
    type: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    event_seq: StrictInt = Field(ge=0)
    session_id: str = Field(min_length=1)
    at: UTCDateTime
    data: dict[str, object]
