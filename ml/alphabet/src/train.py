"""Train the AASL31 image classifier from an approved split manifest.

This CLI mirrors the executed Colab recipe. The original notebook remains the
source of the reported historical results; running this refactor is a new run.
"""

import argparse
import json
from pathlib import Path
import shutil

import pandas as pd
import torch
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader
import yaml

from .dataset import ManifestImageDataset, build_class_to_idx, load_manifest
from .model import build_model
from .preprocessing import build_eval_transform, build_train_transform


def train(config_path, manifest_path, output_dir, data_root=None):
    config_path = Path(config_path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    frame = load_manifest(manifest_path, data_root=data_root)
    class_to_idx = build_class_to_idx(frame["label"])
    train_frame = frame[frame["split"] == "train"].reset_index(drop=True)
    val_frame = frame[frame["split"] == "val"].reset_index(drop=True)
    if train_frame.empty or val_frame.empty:
        raise ValueError("Training and validation splits must both contain images")

    train_aug = config["training"]["augmentation_train_only"]
    train_ds = ManifestImageDataset(
        train_frame, class_to_idx,
        build_train_transform(
            rotation_degrees=train_aug["random_rotation_degrees"],
            brightness=train_aug["brightness_jitter"],
            contrast=train_aug["contrast_jitter"],
        ),
    )
    val_ds = ManifestImageDataset(val_frame, class_to_idx, build_eval_transform())
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    batch_size = int(config["training"]["batch_size"])
    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=2,
        pin_memory=device.type == "cuda",
    )
    val_loader = DataLoader(
        val_ds, batch_size=64, shuffle=False, num_workers=2,
        pin_memory=device.type == "cuda",
    )

    counts = train_frame["label"].value_counts().reindex(class_to_idx.keys()).to_numpy()
    if (counts == 0).any():
        raise ValueError("Every class must have at least one training image")
    class_weights = len(train_frame) / (len(class_to_idx) * counts)
    class_weights = torch.tensor(class_weights, dtype=torch.float32, device=device)

    model = build_model(len(class_to_idx), pretrained=True).to(device)
    criterion = torch.nn.CrossEntropyLoss(weight=class_weights)
    optimizer_name = config["training"]["optimizer"].lower()
    if optimizer_name != "adamw":
        raise ValueError(f"Unsupported optimizer in this baseline: {optimizer_name}")
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=float(config["training"]["learning_rate"])
    )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(config_path, output_dir / config_path.name)
    frame.to_csv(output_dir / "manifest.csv", index=False)
    (output_dir / "class_to_idx.json").write_text(
        json.dumps(class_to_idx, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    history = []
    best_macro_f1 = -1.0
    epochs = int(config["training"]["epochs"])

    for epoch in range(epochs):
        model.train()
        loss_sum = correct = total = 0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            count = labels.size(0)
            loss_sum += loss.item() * count
            correct += (logits.argmax(1) == labels).sum().item()
            total += count

        model.eval()
        val_loss_sum = 0.0
        val_true, val_pred = [], []
        with torch.inference_mode():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                logits = model(images)
                val_loss_sum += criterion(logits, labels).item() * labels.size(0)
                val_pred.extend(logits.argmax(1).cpu().tolist())
                val_true.extend(labels.cpu().tolist())

        row = {
            "epoch": epoch + 1,
            "train_loss": loss_sum / total,
            "train_accuracy": correct / total,
            "val_loss": val_loss_sum / len(val_ds),
            "val_accuracy": sum(a == b for a, b in zip(val_pred, val_true)) / len(val_true),
            "val_macro_f1": f1_score(val_true, val_pred, average="macro", zero_division=0),
        }
        history.append(row)
        pd.DataFrame(history).to_csv(output_dir / "training_history.csv", index=False)
        print(
            f"Epoch {epoch + 1}/{epochs} | train loss: {row['train_loss']:.4f} "
            f"| train acc: {row['train_accuracy']:.3f} | val loss: {row['val_loss']:.4f} "
            f"| val acc: {row['val_accuracy']:.3f} | val macro-F1: {row['val_macro_f1']:.3f}"
        )
        if row["val_macro_f1"] > best_macro_f1:
            best_macro_f1 = row["val_macro_f1"]
            torch.save({
                "model_state_dict": model.state_dict(),
                "class_to_idx": class_to_idx,
                "epoch": epoch + 1,
                "val_accuracy": row["val_accuracy"],
                "val_macro_f1": row["val_macro_f1"],
            }, output_dir / "aasl31_best.pth")
    print(f"Best validation Macro-F1: {best_macro_f1:.4f}")
    print(f"Artifacts saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parents[1]
    parser.add_argument("--config", default=here / "configs" / "aasl31_full_frame_baseline.yaml")
    parser.add_argument("--manifest", required=True, help="CSV split manifest from the approved data run")
    parser.add_argument("--data-root", help="Optional root to rebase manifest paths as label/filename")
    parser.add_argument("--output-dir", default=here / "runs" / "aasl31_full_frame_baseline_v1")
    args = parser.parse_args()
    train(args.config, args.manifest, args.output_dir, args.data_root)


if __name__ == "__main__":
    main()
