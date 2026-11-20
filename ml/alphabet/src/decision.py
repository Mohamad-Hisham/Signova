"""Validation-only score/margin policy search, matching the notebook."""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from .dataset import ManifestImageDataset, load_manifest
from .model import build_model
from .preprocessing import build_eval_transform


def search_validation_thresholds(probabilities, targets, target_precision=0.98, minimum_accepted=50):
    """Mirror the notebook's grid search, maximizing accepted validation count."""
    probabilities = np.asarray(probabilities)
    targets = np.asarray(targets)
    if probabilities.ndim != 2 or len(targets) != probabilities.shape[0]:
        raise ValueError("Expected [samples, classes] probabilities and one target per sample")
    if probabilities.shape[1] < 2 or not np.isfinite(probabilities).all():
        raise ValueError("Need at least two classes and finite probabilities")

    sorted_top2 = np.sort(probabilities, axis=1)[:, -2:]
    top_score = sorted_top2[:, 1]
    margin = sorted_top2[:, 1] - sorted_top2[:, 0]
    predicted = probabilities.argmax(axis=1)
    best = None
    for score_cutoff in np.arange(0.50, 0.991, 0.01):
        for margin_cutoff in np.arange(0.00, 0.501, 0.01):
            accepted = (top_score >= score_cutoff) & (margin >= margin_cutoff)
            count = int(accepted.sum())
            if count < minimum_accepted:
                continue
            precision = float((predicted[accepted] == targets[accepted]).mean())
            if precision >= target_precision:
                candidate = (count, precision, float(score_cutoff), float(margin_cutoff))
                if best is None or candidate[0] > best[0]:
                    best = candidate
    if best is None:
        return {
            "enabled": False,
            "reason": "No thresholds met target precision on validation",
            "target_validation_precision": float(target_precision),
            "status": "exploratory_validation_only",
        }
    count, precision, score_cutoff, margin_cutoff = best
    return {
        "enabled": True,
        "min_score": score_cutoff,
        "min_margin": margin_cutoff,
        "target_validation_precision": float(target_precision),
        "observed_validation_precision": precision,
        "accepted_validation_images": count,
        "validation_coverage": float(count / len(targets)),
        "status": "exploratory_validation_only",
    }


def tune_from_validation(manifest_path, checkpoint_path, data_root=None,
                         target_precision=0.98, minimum_accepted=50):
    """Run the notebook threshold grid on the validation partition only."""
    frame = load_manifest(manifest_path, data_root=data_root)
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    class_to_idx = checkpoint["class_to_idx"]
    classes = [name for name, _ in sorted(class_to_idx.items(), key=lambda pair: pair[1])]
    val_frame = frame[frame["split"] == "val"].reset_index(drop=True)
    if val_frame.empty:
        raise ValueError("The manifest contains no validation images")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(len(classes))
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.to(device).eval()
    loader = DataLoader(
        ManifestImageDataset(val_frame, class_to_idx, build_eval_transform()),
        batch_size=64, shuffle=False, num_workers=2,
        pin_memory=device.type == "cuda",
    )
    probabilities, targets = [], []
    with torch.inference_mode():
        for images, labels in loader:
            probabilities.append(torch.softmax(model(images.to(device)), dim=1).cpu().numpy())
            targets.extend(labels.tolist())
    return search_validation_thresholds(
        np.concatenate(probabilities, axis=0), np.asarray(targets),
        target_precision=target_precision, minimum_accepted=minimum_accepted,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--data-root")
    parser.add_argument("--target-precision", type=float, default=0.98)
    parser.add_argument("--minimum-accepted", type=int, default=50)
    args = parser.parse_args()
    policy = tune_from_validation(
        args.manifest, args.checkpoint, args.data_root,
        args.target_precision, args.minimum_accepted,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(policy, indent=2))
    print("This validation-derived policy is exploratory, not calibrated confidence.")


if __name__ == "__main__":
    main()
