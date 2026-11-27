from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PIL import Image, ImageDraw

from app.models.alphabet import AlphabetAdapter, largest_hand_box
from app.models.base import Prediction

CHECKPOINTS = Path(__file__).resolve().parents[3] / "ml" / "alphabet" / "checkpoints"
CHECKPOINT_SHA256 = "5bc685f101ac1824130cec43af76ccc62f848572b94924cec617b101d31e5e5f"
DETECTOR_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"


def encode(image, format="JPEG"):
    with BytesIO() as output:
        image.save(output, format=format)
        return output.getvalue()


@pytest.fixture
def adapter_stubs():
    probabilities = Mock()
    probabilities.topk.return_value = [0.91, 0.09], [1, 0]
    predictor = SimpleNamespace(
        classes=["Ain", "Alef"], probabilities=Mock(return_value=probabilities)
    )
    find_hand_box = Mock(return_value=(4, 5, 14, 20))
    close_detector = Mock()
    adapter = AlphabetAdapter(
        predictor,
        arabic_labels={"Ain": "ع", "Alef": "ا"},
        find_hand_box=find_hand_box,
        close_detector=close_detector,
        model_version="test-version",
    )
    try:
        yield adapter, predictor, find_hand_box, close_detector
    finally:
        adapter.close()


def test_largest_padded_hand_box_is_clipped():
    small = [SimpleNamespace(x=0.3, y=0.3), SimpleNamespace(x=0.4, y=0.4)]
    large = [SimpleNamespace(x=-0.1, y=-0.1), SimpleNamespace(x=1.1, y=1.1)]
    assert largest_hand_box([small], 320, 240) == (90, 62, 133, 105)
    assert largest_hand_box([small, large], 320, 240) == (0, 0, 320, 240)
    assert (
        largest_hand_box([[], [SimpleNamespace(x=float("nan"), y=1)]], 320, 240) is None
    )


def test_usable_prediction_preserves_mapping_and_uses_rgb_crop(adapter_stubs):
    adapter, predictor, find_hand_box, _ = adapter_stubs
    frame = encode(Image.new("L", (32, 24)))
    result = adapter.predict([frame], [0])

    image = find_hand_box.call_args.args[0]
    crop = predictor.probabilities.call_args.args[0]
    assert (image.size, image.mode) == ((32, 24), "RGB")
    assert (crop.size, crop.mode) == ((10, 15), "RGB")
    assert result == Prediction(
        "Alef", "ا", 0.91, False, True, model_version="test-version"
    )
    assert adapter.labels == (
        {"label_id": "Ain", "text": "ع", "kind": "letter"},
        {"label_id": "Alef", "text": "ا", "kind": "letter"},
    )
    assert adapter.confirmation_policy == "manual"
    assert adapter.window_samples == 1
    assert adapter.required_sample_fps is None


def test_no_hand_skips_classifier_and_is_uncertain(adapter_stubs):
    adapter, predictor, find_hand_box, _ = adapter_stubs
    find_hand_box.return_value = None
    result = adapter.predict([encode(Image.new("RGB", (32, 24)))], [0])

    predictor.probabilities.assert_not_called()
    assert result == Prediction(
        None, None, 0.0, False, False, "no_hand", "test-version"
    )


@pytest.mark.parametrize("scores", [[0.65, 0.35], [0.70, 0.69]])
def test_low_score_or_margin_hides_label(adapter_stubs, scores):
    adapter, predictor, _, _ = adapter_stubs
    predictor.probabilities.return_value.topk.return_value = scores, [0, 1]
    result = adapter.predict([encode(Image.new("RGB", (32, 24)))], [0])

    assert result == Prediction(
        None, None, scores[0], False, False, "uncertain", "test-version"
    )


def test_wrong_window_and_non_jpeg_are_rejected(adapter_stubs):
    adapter, _, find_hand_box, _ = adapter_stubs
    with pytest.raises(ValueError, match="one frame and timestamp"):
        adapter.predict([], [0])
    with pytest.raises(ValueError, match="requires a JPEG"):
        adapter.predict([encode(Image.new("RGB", (32, 24)), "PNG")], [0])
    find_hand_box.assert_not_called()


def test_close_is_idempotent_and_prevents_inference(adapter_stubs):
    adapter, _, find_hand_box, close_detector = adapter_stubs
    adapter.reset_stream("a-prior-stream")
    adapter.close()
    adapter.close()
    with pytest.raises(RuntimeError, match="adapter is closed"):
        adapter.predict([b"data"], [0])
    close_detector.assert_called_once_with()
    find_hand_box.assert_not_called()


def test_class_map_must_match_checkpoint():
    with pytest.raises(ValueError, match="do not match"):
        AlphabetAdapter(
            SimpleNamespace(classes=["Ain", "Alef"]),
            arabic_labels={"Ain": "ع", "Zah": "ظ"},
            find_hand_box=Mock(),
            close_detector=Mock(),
            model_version="test-version",
        )


@pytest.mark.parametrize("incorrect_digest", ["checkpoint", "detector"])
def test_asset_checksum_mismatch_fails_before_model_load(tmp_path, incorrect_digest):
    checkpoint = tmp_path / "model.pth"
    detector = tmp_path / "hand.task"
    checkpoint.write_bytes(b"invalid checkpoint file")
    detector.write_bytes(b"invalid detector file")
    with pytest.raises(ValueError, match="SHA-256"):
        AlphabetAdapter.load(
            checkpoint,
            detector,
            checkpoint_sha256="0" * 64 if incorrect_digest == "checkpoint" else None,
            hand_model_sha256="0" * 64 if incorrect_digest == "detector" else None,
        )


def test_missing_checkpoint_fails_before_importing_model(tmp_path):
    with pytest.raises(FileNotFoundError):
        AlphabetAdapter.load(tmp_path / "missing.pth", tmp_path / "hand.task")


def test_checkpoint_rejects_boolean_class_indices(tmp_path):
    torch = pytest.importorskip("torch")
    pytest.importorskip("torchvision")
    from ml.alphabet.src.predict import AlphabetPredictor

    artifact = tmp_path / "invalid.pth"
    torch.save(
        {
            "class_to_idx": {"Ain": False, "Alef": True},
            "model_state_dict": {"unused": torch.tensor([0.0])},
        },
        artifact,
    )
    with pytest.raises(ValueError, match="integer class indices"):
        AlphabetPredictor(artifact, device="cpu")


@pytest.mark.parametrize("logits", [[[0.0]], [[0.0, float("nan")]]])
def test_predictor_rejects_malformed_model_output(logits):
    torch = pytest.importorskip("torch")
    pytest.importorskip("torchvision")
    from ml.alphabet.src.predict import AlphabetPredictor

    predictor = AlphabetPredictor.__new__(AlphabetPredictor)
    predictor.classes = ["Ain", "Alef"]
    predictor.device = "cpu"
    predictor.transform = Mock(return_value=torch.zeros((3, 224, 224)))
    predictor.model = Mock(return_value=torch.tensor(logits))
    with pytest.raises(ValueError, match="one finite logit per class"):
        predictor.probabilities(Image.new("RGB", (32, 24)))


@pytest.fixture(scope="module")
def local_assets():
    checkpoint = CHECKPOINTS / "aasl31_best.pth"
    hand_model = CHECKPOINTS / "hand_landmarker.task"
    if not checkpoint.is_file() or not hand_model.is_file():
        pytest.skip("local alphabet assets are unavailable")
    pytest.importorskip("torch")
    pytest.importorskip("torchvision")
    pytest.importorskip("mediapipe")
    return checkpoint, hand_model


def test_real_model_assets_load_and_reject_blank_frame(local_assets):
    adapter = AlphabetAdapter.load(
        *local_assets,
        checkpoint_sha256=CHECKPOINT_SHA256,
        hand_model_sha256=DETECTOR_SHA256,
    )
    try:
        assert adapter.model_version.startswith("aasl31-camera-v1-")
        assert len(adapter.labels) == 31
        assert adapter.labels[0] == {"label_id": "Ain", "text": "ع", "kind": "letter"}
        frame = encode(Image.new("RGB", (320, 240)))
        with ThreadPoolExecutor() as worker:
            evidence = worker.submit(adapter.predict, [frame], [0]).result()
        assert evidence == Prediction(
            None, None, 0.0, False, False, "no_hand", adapter.model_version
        )
    finally:
        adapter.close()


def test_adapter_score_matches_checkpoint_on_the_same_crop(local_assets):
    import torch
    from ml.alphabet.src.predict import ARABIC_LABELS, AlphabetPredictor

    checkpoint, _ = local_assets
    torch.set_num_threads(min(4, torch.get_num_threads()))
    predictor = AlphabetPredictor(checkpoint, device="cpu")
    box = (6, 4, 28, 19)
    adapter = AlphabetAdapter(
        predictor,
        arabic_labels=ARABIC_LABELS,
        find_hand_box=lambda _image: box,
        close_detector=Mock(),
        model_version="test-version",
    )
    image = Image.new("RGB", (32, 24), "#eabb95")
    ImageDraw.Draw(image).rectangle((12, 3, 22, 20), fill="#9070b2")
    frame = encode(image)
    with Image.open(BytesIO(frame)) as decoded, torch.inference_mode():
        tensor = predictor.transform(decoded.crop(box).convert("RGB")).unsqueeze(0)
        scores, indices = predictor.model(tensor)[0].softmax(dim=0).topk(2)
    try:
        result = adapter.predict([frame], [0])
        assert result.score == pytest.approx(float(scores[0]), abs=1e-6)
        accepted = float(scores[0]) >= 0.70 and float(scores[0] - scores[1]) >= 0.20
        assert result.usable is accepted
        assert result.label_id == (
            predictor.classes[int(indices[0])] if accepted else None
        )
    finally:
        adapter.close()
