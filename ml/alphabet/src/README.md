# ml/alphabet/src

Owner: **Osama**.

- `dataset.py`: KaggleHub download helper, folder audit, numeric-suffix grouped manifest creation and RGB image loading.
- `model.py`: construct the MobileNetV3-Small model used by the experiment.
- `preprocessing.py`: exact deterministic evaluation/inference transform and train-only augmentation.
- `train.py`: refactored training loop with class-weighted cross entropy and best-validation-Macro-F1 checkpoint selection.
- `evaluate.py`: frozen-checkpoint test metrics, per-class report and confusion evidence.
- `decision.py`: validation probability collection and the notebook's exploratory threshold search; not a calibrated policy.
- `audit_hand_detection.py`: notebook-style per-class MediaPipe hand-detection sample audit; not letter recognition accuracy.
- `predict.py`: side-effect-free single-image predictor.
- `webcam_experiment.py`: MediaPipe hand detection/cropping webcam script, explicitly unvalidated.
- `export.py`: release/export flow remains a scaffold; no production release is approved.

The scripts mirror the executed notebook recipe, but the notebook remains the source of the historical results. The refactored scripts have not been rerun to reproduce the recorded scores. The webcam script accesses the camera and must not be confused with the full-frame test evaluation.
