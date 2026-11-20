"""Exploratory MediaPipe hand-detection audit; not a recognition evaluation."""

import argparse
from collections import Counter
from pathlib import Path
import random

import mediapipe as mp
import numpy as np
from PIL import Image

from .dataset import IMAGE_EXTENSIONS


def audit_hand_detection(data_root, task_path, samples_per_class=10, seed=None):
    """Sample images per class and report whether MediaPipe found a hand."""
    data_root = Path(data_root)
    task_path = Path(task_path)
    if not task_path.is_file():
        raise FileNotFoundError(f"MediaPipe task file not found: {task_path}")
    rng = random.Random(seed)
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(task_path)),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.5,
    )
    success, total = Counter(), Counter()
    with mp.tasks.vision.HandLandmarker.create_from_options(options) as detector:
        for class_dir in sorted(path for path in data_root.iterdir() if path.is_dir()):
            files = [path for path in class_dir.iterdir()
                     if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS]
            sample = rng.sample(files, min(samples_per_class, len(files)))
            for image_path in sample:
                with Image.open(image_path) as image:
                    rgb = np.asarray(image.convert("RGB"))
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                result = detector.detect(mp_image)
                total[class_dir.name] += 1
                if result.hand_landmarks:
                    success[class_dir.name] += 1
    return {name: {"detected": success[name], "sampled": count}
            for name, count in sorted(total.items())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--task", default=Path(__file__).resolve().parents[1] / "checkpoints" / "hand_landmarker.task")
    parser.add_argument("--samples-per-class", type=int, default=10)
    parser.add_argument("--seed", type=int, default=None,
                        help="Leave unset to match the notebook's unseeded random sampling")
    args = parser.parse_args()
    results = audit_hand_detection(args.data_root, args.task, args.samples_per_class, args.seed)
    for label, counts in results.items():
        print(f"{label}: detected {counts['detected']}/{counts['sampled']}")
    total = sum(value["sampled"] for value in results.values())
    detected = sum(value["detected"] for value in results.values())
    print(f"Overall hand detection: {detected}/{total}")
    print("This measures hand detection only, not letter recognition.")


if __name__ == "__main__":
    main()
