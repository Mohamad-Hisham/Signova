# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve typed runtime settings and validated startup policy.
# Owner: Ali.
# Expected inputs: Later environment/origin/artifact/timeout/capacity settings and
#   owner-approved manifests.
# Expected outputs: Future validated immutable configuration or safe startup failure.
# Responsibilities: Validate exact origins, trusted model paths, per-mode requirements, bounded
#   queues/deadlines and manual/automatic policy.
# Connections: main.py, session/recognition services, adapters and public safe catalogue.
# Future implementation: Define Pydantic v2-compatible typed settings after field names and
#   runtime requirements are approved.
# Rules and limitations: No credentials committed, browser-selected model paths, guessed tensor
#   sizes or multiple replicas with RAM sessions.
# Expected tests or acceptance: Incompatible required fps/window rejected; secrets/paths absent
#   from public errors; initial values labeled as starting settings.

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SIGNOVA_",
        env_file=".env",
        extra="forbid",
    )

    app_name: str = "Signova"
    environment: Literal["development", "test", "production"] = "development"

    cors_origins: tuple[str, ...] = ("http://localhost:5173",)
    required_modes: tuple[Literal["alphabet", "word"], ...] = (
        "alphabet",
        "word",
    )

    idle_timeout_seconds: int = Field(default=900, gt=0)
    absolute_timeout_seconds: int = Field(default=3600, gt=0)
    reconnect_grace_seconds: int = Field(default=120, gt=0)
    end_review_seconds: int = Field(default=300, gt=0)
    max_sessions: int = Field(default=20, gt=0)

    max_jpeg_bytes: int = Field(default=163_840, gt=0)
    max_message_bytes: int = Field(default=262_144, gt=0)
    max_jpeg_width: int = Field(default=640, gt=0)
    max_jpeg_height: int = Field(default=480, gt=0)
    max_fps: int = Field(default=10, gt=0)


def get_settings() -> Settings:
    return Settings()
