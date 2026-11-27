"""Read-only recognition model and supported-label catalogues."""

from typing import Annotated, Literal

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from app.config import Settings
from app.models.base import ModelAdapter
from app.schemas.common import ErrorEnvelope, ModelMode
from app.schemas.rest import VocabularyQuery
from app.services.transcript import MAX_TRANSCRIPT_CHARACTERS, MAX_TRANSCRIPT_ITEMS
from app.utilities.errors import ApiError

router = APIRouter(prefix="/api/v1", tags=["catalogues"])


class InputLimits(BaseModel):
    format: Literal["jpeg"] = "jpeg"
    max_width: int
    max_height: int
    max_jpeg_bytes: int
    max_message_bytes: int
    max_fps: int
    required_sample_fps: float | None
    window_samples: int
    mirrored: Literal[False] = False


class TranscriptLimits(BaseModel):
    max_items: int = MAX_TRANSCRIPT_ITEMS
    max_characters: int = MAX_TRANSCRIPT_CHARACTERS


class ModelEntry(BaseModel):
    mode: ModelMode
    model_version: str
    ready: bool
    confirmation_policy: Literal["manual", "automatic_with_manual_fallback"]
    input: InputLimits | None
    transcript_limits: TranscriptLimits


class ModelCatalogue(BaseModel):
    models: list[ModelEntry]


class PublicLabel(BaseModel):
    label_id: str
    text: str
    kind: Literal["word", "letter"]


class Vocabulary(BaseModel):
    mode: ModelMode
    model_version: str
    labels: list[PublicLabel]


def _adapter(request: Request, mode: ModelMode) -> ModelAdapter | None:
    try:
        return request.app.state.adapter_registry.get(mode)
    except KeyError:
        return None


def _model_entry(
    mode: ModelMode, adapter: ModelAdapter | None, settings: Settings
) -> ModelEntry:
    if adapter is None:
        return ModelEntry(
            mode=mode,
            model_version="unavailable",
            ready=False,
            confirmation_policy="manual",
            input=None,
            transcript_limits=TranscriptLimits(),
        )
    return ModelEntry(
        mode=mode,
        model_version=adapter.model_version,
        ready=True,
        confirmation_policy=adapter.confirmation_policy,
        input=InputLimits(
            max_width=settings.max_jpeg_width,
            max_height=settings.max_jpeg_height,
            max_jpeg_bytes=settings.max_jpeg_bytes,
            max_message_bytes=settings.max_message_bytes,
            max_fps=settings.max_fps,
            required_sample_fps=adapter.required_sample_fps,
            window_samples=adapter.window_samples,
        ),
        transcript_limits=TranscriptLimits(),
    )


@router.get("/models", response_model=ModelCatalogue)
async def list_models(request: Request) -> ModelCatalogue:
    """Report available modes, public versions, and capture limits."""
    settings = request.app.state.settings
    modes: tuple[ModelMode, ...] = ("alphabet", "word")
    return ModelCatalogue(
        models=[_model_entry(mode, _adapter(request, mode), settings) for mode in modes]
    )


@router.get(
    "/vocabulary",
    response_model=Vocabulary,
    responses={
        422: {"model": ErrorEnvelope, "description": "Missing or invalid mode"},
        503: {
            "model": ErrorEnvelope,
            "description": "No supported label mapping for this mode",
        },
    },
)
async def list_vocabulary(
    request: Request, query: Annotated[VocabularyQuery, Query()]
) -> Vocabulary:
    """List the public Arabic label mapping for the requested mode."""
    adapter = _adapter(request, query.mode)
    if adapter is None or not adapter.labels:
        raise ApiError(
            503,
            "MODEL_UNAVAILABLE",
            "The label mapping for this recognition mode is unavailable.",
            retryable=True,
        )
    labels = sorted(adapter.labels, key=lambda label: label["label_id"])
    return Vocabulary(
        mode=query.mode,
        model_version=adapter.model_version,
        labels=[PublicLabel.model_validate(label) for label in labels],
    )
