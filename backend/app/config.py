"""Server configuration for the single-process backend."""

from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.common import ModelMode

LOCAL_ALPHABET_ASSETS = (
    Path(__file__).resolve().parents[2] / "ml" / "alphabet" / "checkpoints"
)
LOCAL_ALPHABET_CHECKPOINT = LOCAL_ALPHABET_ASSETS / "aasl31_best.pth"
LOCAL_ALPHABET_HAND_MODEL = LOCAL_ALPHABET_ASSETS / "hand_landmarker.task"
LOCAL_ALPHABET_CHECKPOINT_SHA256 = (
    "5bc685f101ac1824130cec43af76ccc62f848572b94924cec617b101d31e5e5f"
)
LOCAL_ALPHABET_HAND_MODEL_SHA256 = (
    "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SIGNOVA_", env_file=".env", extra="forbid"
    )

    app_name: str = "Signova"
    environment: Literal["development", "test", "production"] = "development"
    cors_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")
    required_modes: tuple[ModelMode, ...] = Field(default=("alphabet",), min_length=1)
    alphabet_checkpoint: Path = LOCAL_ALPHABET_CHECKPOINT
    alphabet_hand_model: Path = LOCAL_ALPHABET_HAND_MODEL
    alphabet_checkpoint_sha256: str | None = Field(
        default=None, pattern=r"^[a-fA-F0-9]{64}$"
    )
    alphabet_hand_model_sha256: str | None = Field(
        default=None, pattern=r"^[a-fA-F0-9]{64}$"
    )

    idle_timeout_seconds: int = Field(default=900, gt=0)
    absolute_timeout_seconds: int = Field(default=3600, gt=0)
    reconnect_grace_seconds: int = Field(default=120, gt=0)
    end_review_seconds: int = Field(default=300, gt=0)
    sweep_interval_seconds: int = Field(default=15, gt=0, le=15)
    max_sessions: int = Field(default=20, gt=0)
    creation_requests_per_minute: int = Field(default=5, gt=0)
    mutation_requests_per_minute: int = Field(default=30, gt=0)
    max_rest_body_bytes: int = Field(default=131_072, gt=0, le=131_072)

    max_jpeg_bytes: int = Field(default=163_840, gt=0, le=163_840)
    max_message_bytes: int = Field(default=262_144, gt=0, le=262_144)
    max_jpeg_width: int = Field(default=640, gt=0, le=640)
    max_jpeg_height: int = Field(default=480, gt=0, le=480)
    max_fps: int = Field(default=10, gt=0, le=10)

    @field_validator("cors_origins")
    @classmethod
    def exact_origins(cls, origins: tuple[str, ...]) -> tuple[str, ...]:
        for origin in origins:
            parts = urlsplit(origin)
            if (
                origin != f"{parts.scheme}://{parts.netloc}"
                or parts.scheme not in {"http", "https"}
                or not parts.hostname
                or parts.username is not None
                or "*" in origin
                or any(character.isspace() for character in origin)
            ):
                raise ValueError("Origins must be exact HTTP(S) origins")
            # Accessing port also rejects malformed or out-of-range values.
            _ = parts.port
        return origins

    @field_validator("required_modes")
    @classmethod
    def distinct_modes(cls, modes: tuple[ModelMode, ...]) -> tuple[ModelMode, ...]:
        if len(modes) != len(set(modes)):
            raise ValueError("Required recognition modes must be unique")
        return modes


def get_settings() -> Settings:
    return Settings()
