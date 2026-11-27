# ml/alphabet

Owner: **Osama**.

This package now records the executed AASL31 full-frame image-classification baseline and its evidence. The Colab notebook remains the source of truth for the training run; the code here now contains a source refactor of dataset preparation, training, evaluation, decision-threshold search, and inference. The webcam hand-crop implementation is in `src/webcam_experiment.py` and has not been independently evaluated.

| Area | Current contents |
|---|---|
| `configs/` | Recorded baseline recipe and split lineage. |
| `src/` | Dataset/split handling, training, evaluation, threshold analysis, hand-detection audit, prediction, and webcam experiment. |
| `reports/` | Model card, run summary and aggregate evaluation evidence. |
| `checkpoints/` | Local checkpoint and class map; ignored by Git and not for ordinary repository commits. |
| `tests/` | Model acceptance plan and links to the backend adapter checks. |

## Current baseline

The model is MobileNetV3-Small trained on 31 image labels from the Kaggle RGB Arabic Alphabets Sign Language dataset. The notebook reports test accuracy **0.9324**, balanced accuracy **0.9307**, and macro-F1 **0.9300** on 1,227 held-out images. The new source refactor has not been run to reproduce those historical scores. The split is disjoint by filename numeric suffix; that suffix has not been verified as signer identity, so signer-independent generalization is not established.

Training was run in Colab on a Tesla T4. The lock file is intentionally not presented as tested; exact local inference latency, webcam accuracy, unknown-sign rejection and temporal/word capability are not established.

## Data and asset handling

The dataset is not copied into this package. The split manifest contains paths and labels for the public source dataset and is retained only as run-lineage evidence. The checkpoint and hand-landmarker asset under `checkpoints/` are ignored local artifacts under the repository's safety policy. The webcam source code is kept in `src/webcam_experiment.py`. Do not force-add them to ordinary Git. The dataset listing identified its license as CC BY-SA 4.0; retain attribution and comply with that license when sharing derived work.

## Single-image inference

From the repository root, with the alphabet dependencies installed:

```python
from pathlib import Path
from PIL import Image
from ml.alphabet.src.predict import AlphabetPredictor

predictor = AlphabetPredictor(Path("ml/alphabet/checkpoints/aasl31_best.pth"))
with Image.open("path/to/sign.jpg") as image:
    result = predictor.predict(image)
print(result["label"], result["arabic"], result["score"])
```

The score is an uncalibrated model score. The separate webcam hand-crop experiment is in `src/webcam_experiment.py` and is not imported by this helper.

Optional camera dependencies are listed in `requirements-webcam.in`; install them in a clean environment to avoid conflicting OpenCV wheels. This optional environment has not been clean-install verified.

## Backend camera integration

The [Signova backend](../../backend/README.md) runs the AASL31 checkpoint on
camera JPEGs using the local hand detector and the existing evaluation
transform. The adapter uses an experimental crop and score filter. It requires
manual confirmation and has no verified webcam accuracy or neutral-sign
recognition.

## Source refactor commands

The code refactor has not been run to reproduce the historical scores. From the repository root, after installing the dependencies, a new run can use the saved split manifest and a local dataset root:

```powershell
python -m ml.alphabet.src.train --manifest ml/alphabet/reports/evidence/aasl31_full_frame_baseline_v1/manifest.csv --data-root "<path to RGB ArSL dataset>" --output-dir ml/alphabet/runs/aasl31_new_run
python -m ml.alphabet.src.evaluate --manifest ml/alphabet/reports/evidence/aasl31_full_frame_baseline_v1/manifest.csv --data-root "<path to RGB ArSL dataset>" --checkpoint ml/alphabet/runs/aasl31_new_run/aasl31_best.pth --output-dir ml/alphabet/runs/aasl31_new_run/evaluation
```

Replace the placeholder with the folder that directly contains the 31 class directories. Runs under `ml/alphabet/runs/` are local and ignored by Git. These commands are documented but were not executed in this migration.

The notebook's validation-only threshold analysis can be repeated with `python -m ml.alphabet.src.decision --manifest <manifest.csv> --data-root "<RGB ArSL dataset>" --checkpoint <checkpoint.pth> --output <decision_policy.json>`. Its output is exploratory because it is derived from validation data.
