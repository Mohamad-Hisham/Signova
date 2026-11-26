# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve Ali common adapter evidence and runtime lifecycle interface.
# Owner: Basel.
# Expected inputs: Owner-specific approved predictor outputs and validated model-bound samples.
# Expected outputs: Future normalized evidence plus model version/readiness/reset semantics.
# Responsibilities: Hide runtime/tensor/class-index differences from networking and explicitly
#   distinguish usable, rejected and evaluated neutral.
# Connections: alphabet.py, word.py, fake.py, model-interface contract and recognition service.
# Future implementation: Declare common interface only after rejected-score and callable-layer
#   decisions are accepted.
# Rules and limitations: No shared hardcoded tensor shape, false neutral, browser schema leakage
#   or enforced identical model preprocessing.
# Expected tests or acceptance: Both adapters map trusted IDs/finite scores and reject invalid
#   output; null raw-score handling follows recorded decision.

import math
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Prediction:
    label_id: str | None
    text: str | None
    score: float
    neutral: bool
    usable: bool
    reason: str | None = None
    model_version: str = ""


class ModelAdapter(Protocol):
    mode: str
    model_version: str

    def predict(self, frames: list[bytes], times_ms: list[float]): ...

    def reset_stream(self, stream_id: str) -> None: ...


def validate_prediction(
    prediction: Prediction,
) -> Prediction:
    if not isinstance(prediction.score, (int, float)):
        raise TypeError("Prediction score must be numeric")
    if isinstance(prediction.score, bool):
        raise TypeError("Prediction score cannot be boolean")
    if not math.isfinite(float(prediction.score)):
        raise ValueError("Prediction score must be finite")
    if not 0 <= float(prediction.score) <= 1:
        raise ValueError("Prediction score must be between 0 and 1")

    if prediction.usable:
        if prediction.label_id is None or prediction.text is None:
            raise ValueError("Usable predictions require label and text")
    else:
        if prediction.label_id is not None or prediction.text is not None:
            raise ValueError("Unusable predictions cannot expose label text")

    if (
        prediction.neutral
        and prediction.usable
        and (prediction.label_id is not None or prediction.text is not None)
    ):
        raise ValueError("Neutral predictions cannot expose word labels")

    return Prediction(
        label_id=prediction.label_id,
        text=prediction.text,
        score=float(prediction.score),
        neutral=prediction.neutral,
        usable=prediction.usable,
        reason=prediction.reason,
        model_version=prediction.model_version,
    )


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, ModelAdapter] = {}

    def register(self, mode: str, adapter: ModelAdapter) -> None:
        if mode not in ("alphabet", "word"):
            raise ValueError("Adapter mode must be alphabet or word")
        if mode in self._adapters:
            raise ValueError("Adapter mode is already registered")
        self._adapters[mode] = adapter

    def get(self, mode: str) -> ModelAdapter:
        adapter = self._adapters.get(mode)
        if adapter is None:
            raise KeyError("Recognition adapter is unavailable")
        return adapter

    def readiness(self) -> dict[str, bool]:
        return {
            "alphabet": "alphabet" in self._adapters,
            "word": "word" in self._adapters,
        }
