from collections import Counter, deque
from pathlib import Path
import time
import urllib.request

import cv2
import mediapipe as mp
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms


# قيم تجريبية مؤقتة لتقليل التوقعات المتذبذبة.
# ليست عتبات ثقة مُعايرة.
MIN_SCORE = 0.70
MIN_MARGIN = 0.20
MIN_STABLE_VOTES = 11
HISTORY_SIZE = 15

ARABIC = {
    "Ain": "ع", "Al": "ال", "Alef": "ا", "Beh": "ب",
    "Dad": "ض", "Dal": "د", "Feh": "ف", "Ghain": "غ",
    "Hah": "ح", "Heh": "ه", "Jeem": "ج", "Kaf": "ك",
    "Khah": "خ", "Laa": "لا", "Lam": "ل", "Meem": "م",
    "Noon": "ن", "Qaf": "ق", "Reh": "ر", "Sad": "ص",
    "Seen": "س", "Sheen": "ش", "Tah": "ط", "Teh": "ت",
    "Teh_Marbuta": "ة", "Thal": "ذ", "Theh": "ث",
    "Waw": "و", "Yeh": "ي", "Zah": "ظ", "Zain": "ز",
}

alphabet_root = Path(__file__).resolve().parents[1]
checkpoint_path = alphabet_root / "checkpoints" / "aasl31_best.pth"
task_path = alphabet_root / "checkpoints" / "hand_landmarker.task"

if not checkpoint_path.exists():
    raise FileNotFoundError(f"مش لاقي الموديل: {checkpoint_path}")

# تنزيل نموذج MediaPipe لكشف اليد إذا لم يكن موجودًا بجانب السكربت
task_url = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
if not task_path.exists():
    print("بنزّل نموذج كشف اليد أول مرة...")
    urllib.request.urlretrieve(task_url, task_path)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
class_to_idx = checkpoint["class_to_idx"]
classes = [
    name for name, idx in sorted(class_to_idx.items(), key=lambda item: item[1])
]

model = models.mobilenet_v3_small(weights=None)
model.classifier[3] = nn.Linear(model.classifier[3].in_features, len(classes))
model.load_state_dict(checkpoint["model_state_dict"])
model.to(device).eval()

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

options = mp.tasks.vision.HandLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(model_asset_path=str(task_path)),
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.55,
    min_hand_presence_confidence=0.55,
    min_tracking_confidence=0.55,
)
landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not camera.isOpened():
    camera.release()
    camera = cv2.VideoCapture(0)

if not camera.isOpened():
    landmarker.close()
    raise RuntimeError(
        "Cannot open camera 0. In WSL, run: python -m ml.alphabet.src.browser_demo "
        "and open http://localhost:8765 in your Windows browser. "
        "Otherwise, check camera permissions and close other camera apps."
    )

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

history = deque(maxlen=HISTORY_SIZE)
last_printed_label = None
last_timestamp_ms = 0


def crop_hand(rgb, hands):
    """يرجع قصاصة اليد الأكبر وصندوقها في إحداثيات الصورة الأصلية."""
    height, width = rgb.shape[:2]
    boxes = []

    for landmarks in hands:
        xs = [point.x * width for point in landmarks]
        ys = [point.y * height for point in landmarks]

        x1, x2 = min(xs), max(xs)
        y1, y2 = min(ys), max(ys)

        # مساحة إضافية حول اليد حتى لا نقصّ الأصابع
        side = max(x2 - x1, y2 - y1) * 1.35
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        left = max(0, int(center_x - side / 2))
        right = min(width, int(center_x + side / 2))
        top = max(0, int(center_y - side / 2))
        bottom = min(height, int(center_y + side / 2))

        if right > left and bottom > top:
            area = (right - left) * (bottom - top)
            boxes.append((area, left, top, right, bottom))

    if not boxes:
        return None, None

    _, left, top, right, bottom = max(boxes)
    return rgb[top:bottom, left:right], (left, top, right, bottom)


print("الكاميرا تعمل. اعرض يدك واضغط q للإغلاق.")
print("لو اليد غير مكتشفة أو التوقع غير ثابت، سيعرض البرنامج حالة عدم يقين.")
print("الجهاز:", device)

try:
    while True:
        ok, frame = camera.read()
        if not ok:
            print("تعذرت قراءة إطار من الكاميرا.")
            break

        rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp_ms = int(time.monotonic() * 1000)
        timestamp_ms = max(timestamp_ms, last_timestamp_ms + 1)
        last_timestamp_ms = timestamp_ms

        hand_result = landmarker.detect_for_video(mp_image, timestamp_ms)
        crop, box = crop_hand(rgb, hand_result.hand_landmarks)

        display = cv2.flip(frame, 1)

        if crop is None:
            history.clear()
            last_printed_label = None
            text = "No hand detected"
            color = (0, 165, 255)
        else:
            left, top, right, bottom = box

            # نعكس إحداثيات الصندوق للعرض المرآتي فقط.
            display_left = frame.shape[1] - right
            display_right = frame.shape[1] - left
            cv2.rectangle(
                display,
                (display_left, top),
                (display_right, bottom),
                (0, 255, 0),
                2,
            )

            tensor = preprocess(Image.fromarray(crop)).unsqueeze(0).to(device)

            with torch.inference_mode():
                probabilities = torch.softmax(model(tensor)[0], dim=0)

            top_values, top_indices = torch.topk(probabilities, k=2)
            score = float(top_values[0].item())
            margin = float((top_values[0] - top_values[1]).item())
            candidate = int(top_indices[0].item())

            frame_passes_filter = score >= MIN_SCORE and margin >= MIN_MARGIN

            if frame_passes_filter:
                history.append((candidate, score))
            else:
                # الإطار غير الواضح يكسر سلسلة الثبات
                history.append(None)

            valid = [item for item in history if item is not None]
            votes = Counter(index for index, _ in valid)

            if len(history) == HISTORY_SIZE and votes:
                stable_idx, vote_count = votes.most_common(1)[0]
            else:
                stable_idx, vote_count = None, 0

            if stable_idx is not None and vote_count >= MIN_STABLE_VOTES:
                label = classes[stable_idx]
                arabic = ARABIC.get(label, "?")
                stable_scores = [
                    value for index, value in valid if index == stable_idx
                ]
                average_score = sum(stable_scores) / len(stable_scores)

                text = f"{label} | score: {average_score:.2f}"
                color = (0, 255, 0)

                if label != last_printed_label:
                    print(
                        f"التوقع: {label} -> {arabic} "
                        f"| model score: {average_score:.3f}"
                    )
                    last_printed_label = label
            else:
                text = "Hand found - uncertain"
                color = (0, 165, 255)
                last_printed_label = None

        cv2.putText(
            display, text, (15, 35),
            cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2, cv2.LINE_AA
        )
        cv2.putText(
            display, "Press q to quit", (15, 70),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA
        )
        cv2.imshow("Signova - Hand crop experiment", display)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.release()
    landmarker.close()
    cv2.destroyAllWindows()
