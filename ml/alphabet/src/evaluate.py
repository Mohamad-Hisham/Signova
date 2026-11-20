"""Evaluate a frozen AASL31 checkpoint on the manifest's test partition."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import torch
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, classification_report,
    confusion_matrix, f1_score,
)
from torch.utils.data import DataLoader

from .dataset import ManifestImageDataset, load_manifest
from .model import build_model
from .preprocessing import build_eval_transform


def evaluate(manifest_path, checkpoint_path, output_dir, data_root=None):
    frame = load_manifest(manifest_path, data_root=data_root)
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    class_to_idx = checkpoint["class_to_idx"]
    classes = [name for name, _ in sorted(class_to_idx.items(), key=lambda pair: pair[1])]
    test_frame = frame[frame["split"] == "test"].reset_index(drop=True)
    if test_frame.empty:
        raise ValueError("The manifest contains no test images")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(len(classes))
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.to(device).eval()
    loader = DataLoader(
        ManifestImageDataset(test_frame, class_to_idx, build_eval_transform()),
        batch_size=64, shuffle=False, num_workers=2,
        pin_memory=device.type == "cuda",
    )
    y_true, y_pred = [], []
    with torch.inference_mode():
        for images, labels in loader:
            logits = model(images.to(device))
            y_pred.extend(logits.argmax(1).cpu().tolist())
            y_true.extend(labels.tolist())

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "checkpoint_epoch": checkpoint.get("epoch"),
        "val_macro_f1": checkpoint.get("val_macro_f1"),
        "test_accuracy": accuracy_score(y_true, y_pred),
        "test_balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "test_macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "test_images": len(y_true),
        "class_count": len(classes),
    }
    pd.DataFrame([metrics]).to_csv(output_dir / "test_metrics.csv", index=False)
    report = classification_report(
        y_true, y_pred, labels=list(range(len(classes))), target_names=classes,
        output_dict=True, zero_division=0,
    )
    pd.DataFrame(report).T.to_csv(output_dir / "test_classification_report.csv")

    counts = confusion_matrix(y_true, y_pred, labels=list(range(len(classes))))
    normalized = confusion_matrix(
        y_true, y_pred, labels=list(range(len(classes))), normalize="true"
    )
    pd.DataFrame(counts, index=classes, columns=classes).to_csv(
        output_dir / "test_confusion_matrix_counts.csv"
    )
    fig, axes = plt.subplots(1, 2, figsize=(23, 10))
    sns.heatmap(counts, cmap="Blues", xticklabels=classes, yticklabels=classes, ax=axes[0])
    axes[0].set_title("Test confusion matrix — counts")
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("Actual")
    sns.heatmap(
        normalized * 100, cmap="Blues", vmin=0, vmax=100,
        xticklabels=classes, yticklabels=classes, ax=axes[1],
    )
    axes[1].set_title("Test confusion matrix — row percentages")
    axes[1].set_xlabel("Predicted")
    axes[1].set_ylabel("Actual")
    for axis in axes:
        axis.tick_params(axis="x", rotation=90, labelsize=7)
        axis.tick_params(axis="y", rotation=0, labelsize=7)
    fig.tight_layout()
    fig.savefig(output_dir / "test_confusion_matrix.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    history_path = Path(checkpoint_path).parent / "training_history.csv"
    if history_path.is_file():
        history = pd.read_csv(history_path)
        fig, axes = plt.subplots(1, 3, figsize=(17, 5))
        axes[0].plot(history["epoch"], history["train_loss"], marker="o", label="Train")
        axes[0].plot(history["epoch"], history["val_loss"], marker="o", label="Validation")
        axes[0].set_title("Loss")
        axes[0].set_xlabel("Epoch")
        axes[0].grid(True)
        axes[0].legend()
        axes[1].plot(history["epoch"], history["train_accuracy"], marker="o", label="Train")
        axes[1].plot(history["epoch"], history["val_accuracy"], marker="o", label="Validation")
        axes[1].set_title("Accuracy")
        axes[1].set_xlabel("Epoch")
        axes[1].grid(True)
        axes[1].legend()
        axes[2].plot(history["epoch"], history["val_macro_f1"], marker="o", color="purple")
        axes[2].set_title("Validation Macro-F1")
        axes[2].set_xlabel("Epoch")
        axes[2].grid(True)
        fig.tight_layout()
        fig.savefig(output_dir / "training_curves.png", dpi=180, bbox_inches="tight")
        plt.close(fig)
    print(metrics)
    print(f"Per-class report and confusion evidence saved to: {output_dir}")
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data-root")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    evaluate(args.manifest, args.checkpoint, args.output_dir, args.data_root)


if __name__ == "__main__":
    main()
