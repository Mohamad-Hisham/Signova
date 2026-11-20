"""Side-effect-free single-image inference for a local AASL31 checkpoint.

The returned softmax score is a model score, not calibrated confidence. This
module intentionally does not apply a rejection threshold or claim webcam
performance; those require separately validated policies.
"""

from pathlib import Path

import torch
from PIL import Image

from .model import build_model
from .preprocessing import as_rgb, build_eval_transform

ARABIC_LABELS = {
    "Ain": "ع", "Al": "ال", "Alef": "ا", "Beh": "ب",
    "Dad": "ض", "Dal": "د", "Feh": "ف", "Ghain": "غ",
    "Hah": "ح", "Heh": "ه", "Jeem": "ج", "Kaf": "ك",
    "Khah": "خ", "Laa": "لا", "Lam": "ل", "Meem": "م",
    "Noon": "ن", "Qaf": "ق", "Reh": "ر", "Sad": "ص",
    "Seen": "س", "Sheen": "ش", "Tah": "ط", "Teh": "ت",
    "Teh_Marbuta": "ة", "Thal": "ذ", "Theh": "ث",
    "Waw": "و", "Yeh": "ي", "Zah": "ظ", "Zain": "ز",
}


class AlphabetPredictor:
    """Load the trained full-frame checkpoint and predict one RGB image."""

    def __init__(self, checkpoint_path, device=None):
        self.checkpoint_path = Path(checkpoint_path)
        if not self.checkpoint_path.is_file():
            raise FileNotFoundError(f"Checkpoint not found: {self.checkpoint_path}")

        self.device = torch.device(
            device if device is not None else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        checkpoint = torch.load(
            self.checkpoint_path, map_location=self.device, weights_only=True
        )
        class_to_idx = checkpoint.get("class_to_idx")
        state_dict = checkpoint.get("model_state_dict")
        if not isinstance(class_to_idx, dict) or not state_dict:
            raise ValueError("Checkpoint is missing class_to_idx or model_state_dict")

        ordered = sorted(class_to_idx.items(), key=lambda item: item[1])
        indices = [index for _, index in ordered]
        if indices != list(range(len(ordered))):
            raise ValueError("Checkpoint class indices must be contiguous and zero-based")
        self.classes = [name for name, _ in ordered]
        self.transform = build_eval_transform()
        self.model = build_model(len(self.classes))
        self.model.load_state_dict(state_dict, strict=True)
        self.model.to(self.device).eval()

    @torch.inference_mode()
    def predict(self, image: Image.Image) -> dict:
        """Return the top class and its uncalibrated softmax model score."""
        tensor = self.transform(as_rgb(image)).unsqueeze(0).to(self.device)
        probabilities = torch.softmax(self.model(tensor)[0], dim=0)
        index = int(probabilities.argmax().item())
        label = self.classes[index]
        return {
            "class_index": index,
            "label": label,
            "arabic": ARABIC_LABELS.get(label),
            "score": float(probabilities[index].item()),
        }
