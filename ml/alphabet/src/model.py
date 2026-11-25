"""MobileNetV3-Small architecture used by the AASL31 baseline."""

from torch import nn
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small


def build_model(num_classes: int, pretrained: bool = False):
    """Build the trained architecture; optionally initialize ImageNet weights."""
    if not isinstance(num_classes, int) or num_classes < 1:
        raise ValueError("num_classes must be a positive integer")
    weights = MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
    model = mobilenet_v3_small(weights=weights)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    return model
