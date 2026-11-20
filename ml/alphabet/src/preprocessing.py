"""Deterministic and train-only transforms for the AASL31 baseline."""

from PIL import Image
from torchvision import transforms

IMAGE_SIZE = (224, 224)
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def build_eval_transform():
    """Deterministic RGB resize/tensor/normalization used in val/test/serving."""
    return transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def build_train_transform(rotation_degrees=8, brightness=0.15, contrast=0.15):
    """Notebook training transform; stochastic augmentation is train-only."""
    return transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.RandomRotation(rotation_degrees),
        transforms.ColorJitter(brightness=brightness, contrast=contrast),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def as_rgb(image: Image.Image) -> Image.Image:
    """Convert a PIL image to RGB, matching the notebook loader."""
    if not isinstance(image, Image.Image):
        raise TypeError("image must be a PIL.Image.Image")
    return image.convert("RGB")
