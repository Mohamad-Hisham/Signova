"""Behavior checks for the local browser demo, without requiring a camera."""

from collections import deque
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from PIL import Image
import torch

from ml.alphabet.src.browser_demo import CameraPredictor, hand_box
from ml.alphabet.src.preprocessing import build_eval_transform


class BrowserDemoTests(unittest.TestCase):
    def setUp(self):
        self.engine = CameraPredictor.__new__(CameraPredictor)
        self.hand = [SimpleNamespace(x=0.2, y=0.2), SimpleNamespace(x=0.8, y=0.8)]
        self.engine.detector = Mock()
        self.engine.detector.detect_for_video.return_value = SimpleNamespace(hand_landmarks=[self.hand])
        self.model = Mock(return_value=torch.tensor([[8.0, 0.0]]))
        self.engine.predictor = SimpleNamespace(
            model=self.model, transform=build_eval_transform(), device="cpu", classes=["Ain", "Alef"]
        )
        self.engine.history = deque(maxlen=15)
        self.engine.last_timestamp = 0
        self.engine.last_frame_at = 0
        self.image = Image.new("RGB", (320, 240), "white")

    def test_largest_hand_box_is_clipped_to_frame(self):
        small = [SimpleNamespace(x=0.3, y=0.3), SimpleNamespace(x=0.4, y=0.4)]
        large = [SimpleNamespace(x=-0.1, y=-0.1), SimpleNamespace(x=1.1, y=1.1)]
        self.assertEqual(hand_box([small, large], 320, 240), (0, 0, 320, 240))
        self.assertIsNone(hand_box([], 320, 240))

    def test_stable_letter_requires_full_history(self):
        for _ in range(14):
            self.assertEqual(self.engine.process(self.image)["status"], "uncertain")
        result = self.engine.process(self.image)
        self.assertEqual(result["status"], "stable")
        self.assertEqual(result["prediction"]["label"], "Ain")
        self.assertEqual(result["prediction"]["arabic"], "ع")
        self.assertTrue(all(0 <= coordinate <= 1 for coordinate in result["box"]))
        timestamps = [call.args[1] for call in self.engine.detector.detect_for_video.call_args_list]
        self.assertTrue(all(a < b for a, b in zip(timestamps, timestamps[1:])))

    def test_low_margin_does_not_produce_a_stable_letter(self):
        self.model.return_value = torch.tensor([[0.0, 0.0]])
        for _ in range(16):
            result = self.engine.process(self.image)
        self.assertEqual(result["status"], "uncertain")
        self.assertIsNone(result["prediction"])

    def test_no_hand_clears_votes_without_running_classifier(self):
        self.engine.history.append((0, 0.99))
        self.engine.detector.detect_for_video.return_value = SimpleNamespace(hand_landmarks=[])
        self.assertEqual(self.engine.process(self.image)["status"], "no_hand")
        self.assertEqual(len(self.engine.history), 0)
        self.model.assert_not_called()

    def test_pause_clears_old_votes(self):
        self.engine.history.extend([(0, 0.99)] * 14)
        self.engine.last_frame_at = 0
        self.assertEqual(self.engine.process(self.image)["status"], "uncertain")
        self.assertEqual(len(self.engine.history), 1)


if __name__ == "__main__":
    torch.set_num_threads(2)
    unittest.main()
