"""Manifest creation and image loading for the AASL31 dataset."""

from pathlib import Path
import re

import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLITS = ("train", "val", "test")



def download_kaggle_dataset(output_dir=None):
    """Download the notebook's Kaggle dataset using the caller's Kaggle access."""
    import kagglehub
    kwargs = {"output_dir": str(output_dir)} if output_dir is not None else {}
    return Path(kagglehub.dataset_download(
        "muhammadalbrham/rgb-arabic-alphabets-sign-language-dataset", **kwargs
    ))


def audit_class_folders(data_root):
    """Return image counts per folder and numeric suffixes shared across labels."""
    from collections import defaultdict
    data_root = Path(data_root)
    counts = {}
    number_to_labels = defaultdict(set)
    for class_dir in sorted(path for path in data_root.iterdir() if path.is_dir()):
        files = [path for path in class_dir.iterdir()
                 if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS]
        counts[class_dir.name] = len(files)
        for path in files:
            match = re.search(r"_(\d+)$", path.stem)
            if match:
                number_to_labels[match.group(1)].add(class_dir.name)
    shared = {number: sorted(labels) for number, labels in number_to_labels.items()
              if len(labels) > 1}
    return {"class_image_counts": counts, "shared_numeric_suffixes": shared}

def create_grouped_manifest(data_root, output_path, random_state=42):
    """Create the notebook's 70/15/15 split, grouping by filename suffix.

    A numeric suffix is only a grouping key; this function does not infer that
    it identifies a signer.
    """
    data_root = Path(data_root)
    records = []
    for class_dir in sorted(path for path in data_root.iterdir() if path.is_dir()):
        for image_path in sorted(class_dir.iterdir()):
            if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            match = re.search(r"_(\d+)$", image_path.stem)
            if not match:
                raise ValueError(f"Filename has no trailing numeric group: {image_path.name}")
            records.append({
                "image_path": str(image_path),
                "label": class_dir.name,
                "group_id": match.group(1),
            })

    frame = pd.DataFrame(records)
    if frame.empty:
        raise ValueError(f"No supported images found under {data_root}")
    groups = sorted(frame["group_id"].unique())
    train_groups, remaining = train_test_split(
        groups, test_size=0.30, random_state=random_state
    )
    val_groups, test_groups = train_test_split(
        remaining, test_size=0.50, random_state=random_state
    )
    group_to_split = {group: "train" for group in train_groups}
    group_to_split.update({group: "val" for group in val_groups})
    group_to_split.update({group: "test" for group in test_groups})
    frame["split"] = frame["group_id"].map(group_to_split)

    sets = {name: set(frame.loc[frame["split"] == name, "group_id"]) for name in SPLITS}
    if any(sets[a] & sets[b] for i, a in enumerate(SPLITS) for b in SPLITS[i + 1:]):
        raise RuntimeError("Numeric groups overlap across splits")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return frame


def load_manifest(manifest_path, data_root=None):
    """Read and validate a split manifest; optionally rebase image paths."""
    frame = pd.read_csv(manifest_path)
    required = {"image_path", "label", "group_id", "split"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Manifest is missing columns: {sorted(missing)}")
    if frame.empty or not set(frame["split"].unique()).issubset(SPLITS):
        raise ValueError("Manifest is empty or contains an unsupported split value")
    group_split_counts = frame.groupby("group_id")["split"].nunique()
    if (group_split_counts > 1).any():
        raise ValueError("A numeric filename group occurs in more than one split")
    if data_root is not None:
        data_root = Path(data_root)
        frame["image_path"] = [
            str(data_root / str(label) / Path(str(path)).name)
            for label, path in zip(frame["label"], frame["image_path"])
        ]
    missing_files = [path for path in frame["image_path"] if not Path(path).is_file()]
    if missing_files:
        raise FileNotFoundError(
            f"{len(missing_files)} manifest images are missing; example: {missing_files[0]}"
        )
    return frame


def build_class_to_idx(labels):
    """Create the lexicographically sorted class mapping used in the notebook."""
    classes = sorted(set(labels))
    if not classes:
        raise ValueError("At least one class label is required")
    return {label: index for index, label in enumerate(classes)}


class ManifestImageDataset(Dataset):
    """Load RGB images and integer targets from a manifest DataFrame."""

    def __init__(self, frame, class_to_idx, transform):
        self.frame = frame.reset_index(drop=True)
        self.class_to_idx = class_to_idx
        self.transform = transform
        unknown = set(self.frame["label"]) - set(class_to_idx)
        if unknown:
            raise ValueError(f"Labels are absent from class map: {sorted(unknown)}")

    def __len__(self):
        return len(self.frame)

    def __getitem__(self, index):
        row = self.frame.iloc[index]
        with Image.open(row["image_path"]) as image:
            image = image.convert("RGB")
        return self.transform(image), int(self.class_to_idx[row["label"]])
