"""Live alphabet inference using the AASL31 checkpoint and a local hand detector."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from hashlib import file_digest, sha256
from io import BytesIO
from math import isfinite
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Protocol

from PIL import Image

from app.models.base import Prediction

if TYPE_CHECKING:
    from ml.alphabet.src.predict import AlphabetPredictor


MIN_SCORE = 0.70
MIN_MARGIN = 0.20

HandBox = tuple[int, int, int, int]


class Landmark(Protocol):
    x: float
    y: float


def largest_hand_box(
    hands: Sequence[Sequence[Landmark]], width: int, height: int
) -> HandBox | None:
    """Find the largest padded hand box within the camera image."""
    boxes = []
    for hand in hands:
        if not hand or not all(
            isfinite(point.x) and isfinite(point.y) for point in hand
        ):
            continue
        xs = [point.x * width for point in hand]
        ys = [point.y * height for point in hand]
        side = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.35
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
        left, top = max(0, int(cx - side / 2)), max(0, int(cy - side / 2))
        right = min(width, int(cx + side / 2))
        bottom = min(height, int(cy + side / 2))
        if right > left and bottom > top:
            area = (right - left) * (bottom - top)
            boxes.append((area, (left, top, right, bottom)))
    return max(boxes)[1] if boxes else None


def _asset_digest(path: Path, expected: str | None) -> str:
    with path.open("rb") as artifact:
        digest = file_digest(artifact, "sha256").hexdigest()
    if expected is not None and digest != expected.lower():
        raise ValueError("Alphabet artifact SHA-256 does not match its configuration")
    return digest


class AlphabetAdapter:
    mode = "alphabet"
    confirmation_policy = "manual"
    window_samples = 1
    required_sample_fps = None

    def __init__(
        self,
        predictor: AlphabetPredictor,
        *,
        arabic_labels: Mapping[str, str],
        find_hand_box: Callable[[Image.Image], HandBox | None],
        close_detector: Callable[[], None],
        model_version: str,
    ):
        if len(predictor.classes) < 2 or set(predictor.classes) != arabic_labels.keys():
            raise ValueError(
                "Alphabet checkpoint classes do not match the Arabic class map"
            )
        self.model_version = model_version
        self.labels = tuple(
            {"label_id": label, "text": arabic_labels[label], "kind": "letter"}
            for label in sorted(predictor.classes)
        )
        self._arabic_labels = dict(arabic_labels)
        self._predictor = predictor
        self._find_hand_box = find_hand_box
        self._close_detector = close_detector
        self._inference_lock = Lock()
        self._closed = False

    @classmethod
    def load(
        cls,
        checkpoint_path: Path,
        hand_model_path: Path,
        *,
        checkpoint_sha256: str | None = None,
        hand_model_sha256: str | None = None,
    ) -> AlphabetAdapter:
        checkpoint_digest = _asset_digest(checkpoint_path, checkpoint_sha256)
        detector_digest = _asset_digest(hand_model_path, hand_model_sha256)

        import mediapipe as mp
        import numpy as np
        import torch
        from ml.alphabet.src.predict import ARABIC_LABELS, AlphabetPredictor

        torch.set_num_threads(min(4, torch.get_num_threads()))
        predictor = AlphabetPredictor(checkpoint_path, device="cpu")
        warmup = Image.new("RGB", (224, 224))
        predictor.probabilities(warmup)

        # Stateless image mode keeps one session's hand tracking out of others.
        detector = mp.tasks.vision.HandLandmarker.create_from_options(
            mp.tasks.vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(
                    model_asset_path=str(hand_model_path),
                ),
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
                num_hands=2,
                min_hand_detection_confidence=0.55,
                min_hand_presence_confidence=0.55,
            )
        )

        def find_hand_box(image: Image.Image) -> HandBox | None:
            media_image = mp.Image(
                image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(image)
            )
            result = detector.detect(media_image)
            return largest_hand_box(result.hand_landmarks, *image.size)

        version_digest = sha256(f"{checkpoint_digest}:{detector_digest}".encode())
        try:
            find_hand_box(warmup)
            return cls(
                predictor,
                arabic_labels=ARABIC_LABELS,
                find_hand_box=find_hand_box,
                close_detector=detector.close,
                model_version=f"aasl31-camera-v1-{version_digest.hexdigest()[:16]}",
            )
        except BaseException:
            detector.close()
            raise

    def predict(self, frames: list[bytes], times_ms: list[float]) -> Prediction:
        if len(frames) != 1 or len(times_ms) != 1:
            raise ValueError("Alphabet recognition requires one frame and timestamp")
        with self._inference_lock:
            if self._closed:
                raise RuntimeError("Alphabet adapter is closed")
            with Image.open(BytesIO(frames[0])) as encoded:
                if encoded.format != "JPEG":
                    raise ValueError("Alphabet recognition requires a JPEG frame")
                image = encoded.convert("RGB")
            box = self._find_hand_box(image)
            if box is None:
                return self._reject("no_hand", 0.0)

            scores, indices = self._predictor.probabilities(image.crop(box)).topk(2)
            score = float(scores[0])
            if score < MIN_SCORE or float(scores[0] - scores[1]) < MIN_MARGIN:
                return self._reject("uncertain", score)

            label = self._predictor.classes[int(indices[0])]
            return Prediction(
                label_id=label,
                text=self._arabic_labels[label],
                score=score,
                neutral=False,
                usable=True,
                model_version=self.model_version,
            )

    def _reject(self, reason: str, score: float) -> Prediction:
        return Prediction(
            label_id=None,
            text=None,
            score=score,
            neutral=False,
            usable=False,
            reason=reason,
            model_version=self.model_version,
        )

    def reset_stream(self, stream_id: str) -> None:
        """The adapter has no per-stream state to reset."""

    def close(self) -> None:
        with self._inference_lock:
            if not self._closed:
                self._closed = True
                self._close_detector()
