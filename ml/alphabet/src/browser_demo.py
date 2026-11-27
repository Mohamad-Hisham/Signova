"""Local browser-camera demo; Python never opens a native camera device.

Run from the repository root: python -m ml.alphabet.src.browser_demo
The browser sends JPEG frames to this loopback-only server. Frames stay in
memory. Hand crops and exploratory stability filters mirror the native demo;
webcam accuracy and the rejection thresholds have not been validated.
"""

import argparse
from collections import Counter, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
from pathlib import Path
import time
import traceback
from threading import Lock

import mediapipe as mp
import numpy as np
from PIL import Image, UnidentifiedImageError
import torch

from .predict import ARABIC_LABELS, AlphabetPredictor


ALPHABET_ROOT = Path(__file__).resolve().parents[1]
MAX_FRAME_BYTES = 2 * 1024 * 1024


def hand_box(landmarks, width, height):
    """Return the largest padded, square hand box, clipped to the frame."""
    boxes = []
    for hand in landmarks:
        xs = [point.x * width for point in hand]
        ys = [point.y * height for point in hand]
        side = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.35
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        left, top = max(0, int(cx - side / 2)), max(0, int(cy - side / 2))
        right, bottom = min(width, int(cx + side / 2)), min(height, int(cy + side / 2))
        if right > left and bottom > top:
            boxes.append(((right - left) * (bottom - top), (left, top, right, bottom)))
    return max(boxes)[1] if boxes else None


class CameraPredictor:
    def __init__(self, checkpoint, hand_model):
        if not hand_model.is_file():
            raise FileNotFoundError(f"Hand detector not found: {hand_model}")
        self.predictor = AlphabetPredictor(checkpoint)
        self.detector = mp.tasks.vision.HandLandmarker.create_from_options(
            mp.tasks.vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(hand_model)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,
                num_hands=2,
                min_hand_detection_confidence=0.55,
                min_hand_presence_confidence=0.55,
                min_tracking_confidence=0.55,
            )
        )
        self.history = deque(maxlen=15)
        self.last_timestamp = 0
        self.last_frame_at = 0.0

    @torch.inference_mode()
    def process(self, image):
        now = time.monotonic()
        if now - self.last_frame_at > 2:
            self.history.clear()
        self.last_frame_at = now
        timestamp = max(int(now * 1000), self.last_timestamp + 1)
        self.last_timestamp = timestamp
        rgb = np.ascontiguousarray(image.convert("RGB"))
        detected = self.detector.detect_for_video(
            mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp
        )
        box = hand_box(detected.hand_landmarks, image.width, image.height)
        if box is None:
            self.history.clear()
            return {"status": "no_hand", "box": None, "prediction": None}

        predictor = self.predictor
        tensor = predictor.transform(image.crop(box).convert("RGB"))
        probabilities = torch.softmax(predictor.model(tensor.unsqueeze(0).to(predictor.device))[0], dim=0)
        scores, indices = probabilities.topk(2)
        score = float(scores[0])
        candidate = int(indices[0])
        passes = score >= 0.70 and float(scores[0] - scores[1]) >= 0.20
        self.history.append((candidate, score) if passes else None)
        valid = [entry for entry in self.history if entry is not None]
        votes = Counter(index for index, _ in valid)
        stable, count = votes.most_common(1)[0] if votes else (None, 0)
        prediction = None
        if len(self.history) == self.history.maxlen and count >= 11:
            label = predictor.classes[stable]
            stable_scores = [value for index, value in valid if index == stable]
            prediction = {
                "label": label,
                "arabic": ARABIC_LABELS.get(label, "?"),
                "score": sum(stable_scores) / len(stable_scores),
            }
        return {
            "status": "stable" if prediction else "uncertain",
            "box": [box[0] / image.width, box[1] / image.height,
                    box[2] / image.width, box[3] / image.height],
            "prediction": prediction,
        }

    def close(self):
        self.detector.close()


def make_handler(predictor):
    page = Path(__file__).with_name("browser_demo.html").read_bytes()
    inference_lock = Lock()

    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, body, content_type="application/json; charset=utf-8"):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/":
                self.reply(200, page, "text/html; charset=utf-8")
            else:
                self.reply(404, b'{"error":"Not found"}')

        def do_POST(self):
            # Allow only this page to submit camera frames to the local model.
            origin = self.headers.get("Origin")
            host = self.headers.get("Host")
            allowed_hosts = {f"localhost:{self.server.server_port}",
                             f"127.0.0.1:{self.server.server_port}"}
            if host not in allowed_hosts or origin != f"http://{host}":
                self.reply(403, b'{"error":"Open the demo using its localhost URL"}')
                return
            if self.path == "/reset":
                with inference_lock:
                    predictor.history.clear()
                self.reply(200, b"{}")
                return
            if self.path != "/predict":
                self.reply(404, b'{"error":"Not found"}')
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= MAX_FRAME_BYTES:
                    self.reply(413, b'{"error":"Frame must be between 1 byte and 2 MB"}')
                    return
                if self.headers.get("Content-Type") != "image/jpeg":
                    self.reply(415, b'{"error":"Expected a JPEG frame"}')
                    return
                with Image.open(BytesIO(self.rfile.read(length))) as image:
                    if image.format != "JPEG" or max(image.size) > 1280:
                        raise ValueError("Expected a JPEG no larger than 1280 pixels per side")
                    with inference_lock:
                        result = predictor.process(image.convert("RGB"))
                self.reply(200, json.dumps(result, ensure_ascii=False).encode("utf-8"))
            except (ValueError, UnidentifiedImageError, OSError) as error:
                self.reply(400, json.dumps({"error": str(error)}).encode())
            except Exception:
                traceback.print_exc()
                self.reply(500, b'{"error":"Inference failed; check the terminal"}')

        def log_message(self, format, *args):
            # Avoid a terminal log line for every camera frame.
            if len(args) > 1 and str(args[1]) != "200":
                super().log_message(format, *args)

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    torch.set_num_threads(4)
    predictor = CameraPredictor(
        ALPHABET_ROOT / "checkpoints/aasl31_best.pth",
        ALPHABET_ROOT / "checkpoints/hand_landmarker.task",
    )
    try:
        with ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(predictor)) as server:
            print(f"\nOpen http://localhost:{server.server_port} in your Windows browser.", flush=True)
            print(f"Model device: {predictor.predictor.device}. Press Ctrl+C to stop.", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        print("\nDemo stopped.")
    finally:
        predictor.close()


if __name__ == "__main__":
    main()
