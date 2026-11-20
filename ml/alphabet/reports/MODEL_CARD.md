# Signova AASL31 alphabet model card

**Owner:** Osama  
**Status:** Trained and evaluated as a static full-frame image-classification baseline. The local checkpoint is available; a production release and live-camera hand-crop performance have not been accepted or independently validated.

## Identity and intended use

- **Experiment/version:** `aasl31_full_frame_baseline_v1`
- **Architecture:** torchvision MobileNetV3-Small, initialized from `MobileNet_V3_Small_Weights.DEFAULT`, with a 31-class output layer.
- **Checkpoint:** local-only file `checkpoints/aasl31_best.pth` (excluded from Git); SHA-256 `5bc685f101ac1824130cec43af76ccc62f848572b94924cec617b101d31e5e5f`. The checkpoint is ignored by Git under repository policy.
- **Intended scope:** classify one static RGB image into one of the 31 dataset labels as a graduation-project prototype.
- **Out of scope:** continuous sign-language translation, words/sentences, temporal signs, neutral/unknown-sign detection, guaranteed signer-independent operation, and production accessibility claims.
- **Exact class order:** recorded in local-only file `checkpoints/class_to_idx.json` (excluded from Git).

## Input, preprocessing and output

- Input: one PIL image, converted to RGB; deterministic resize to `224×224`, tensor conversion, ImageNet normalization (mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`).
- Model tensor: `[N, 3, 224, 224]`, float32.
- Output: 31 logits; inference applies softmax for ranking. A softmax score is **not calibrated confidence** and does not by itself mean the prediction is reliable.
- Handedness/orientation policy: no separate hand-orientation normalization was recorded for the full-frame model.
- The production inference helper returns the top class and score; it does not currently provide validated unknown-sign rejection.

## Data and provenance

- Source: Kaggle dataset `muhammadalbrham/rgb-arabic-alphabets-sign-language-dataset`; the dataset listing used in the project identifies CC BY-SA 4.0. Retain attribution and comply with the license when redistributing derived work.
- Dataset size: 7,856 RGB images in 31 labels.
- Split method: filename numeric suffix groups, seed 42; train 5,456, validation 1,173, test 1,227. The notebook found zero group overlap between partitions.
- **Limitation:** numeric suffixes were not verified as signer IDs. Therefore the experiment does not establish independent-signer generalization.
- Pretraining: torchvision default MobileNetV3-Small weights. The precise package/weight revision was not pinned in the run record.
- The executed training notebook is referenced as `Untitled13.ipynb`; source modules now contain a refactor of the notebook workflow, not a separately rerun experiment. The notebook is the source of truth for this card's historical metrics. SHA-256 `1d9ac118cba4ff6e6cef68df0ccd62fc40d77a221e341edac25d14d5ff0e3281`. Aggregate run evidence is in [`RUN_SUMMARY_AASL31.md`](RUN_SUMMARY_AASL31.md) and `evidence/aasl31_full_frame_baseline_v1/`.

## Training and selection

- Hardware: Google Colab Tesla T4.
- 12 epochs; batch size 32; AdamW with learning rate `1e-4`.
- Loss: class-weighted cross entropy, with weights `total_images / (class_count × class_images)`.
- Training-only augmentation: random rotation up to 8 degrees and brightness/contrast jitter of 0.15.
- Selection: highest validation Macro-F1; selected epoch 11.
- Training seed and a fully pinned environment lock were not recorded.

## Recognition evidence

| Metric | Validation/model selection | Test |
|---|---:|---:|
| Accuracy | 0.935 (reported) | 0.9324 |
| Macro-F1 | 0.9336 (best, epoch 11) | 0.9300 |
| Balanced accuracy | Not recorded as selection metric | 0.9307 |
| Support | 1,173 | 1,227 |

Per-class precision, recall, F1/support, confusion matrix counts, training history and curves are in `evidence/aasl31_full_frame_baseline_v1/`. Lower test F1 values include Dal (0.824), Qaf (0.844), Zah (0.848), Hah (0.867), Tah (0.868), Thal (0.875), and Theh (0.899); review the full report before relying on any class-specific result.

A validation threshold search recorded score ≥0.89 and margin ≥0.00, with observed precision 0.9802 on 1,009/1,173 validation images (coverage 0.86). This is exploratory: the validation data also selected the checkpoint, and the score was not calibrated. It is not a test-set result or an approved release policy.

## Live capability and webcam experiment

The evaluated model was trained on full-frame images. A separate MediaPipe hand-detection/crop webcam experiment is preserved in [`../src/webcam_experiment.py`](../src/webcam_experiment.py), with its local task/checkpoint assets under `../checkpoints/`. It applies the full-frame checkpoint to cropped hand images, which changes the input distribution. No independent test of that crop pipeline or live-camera recognition accuracy has been completed. Its temporary score/margin/frame-vote filters are not calibrated thresholds.

## Performance and integration

- Training hardware is recorded as Tesla T4. Local inference latency, p50/p95, memory, concurrency and hardware parity have not been measured.
- The single-image predictor is implemented in `src/predict.py`; the webcam experiment is separate.
- No backend parity, golden-fixture acceptance, safe-unavailable review or production release signoff is recorded.

## Limitations and maintenance

Results are limited to the source dataset, its recorded split, and static image classification. Background, camera, lighting, signer, framing and hand-crop shifts may reduce performance. The split does not establish signer independence. Weak classes and false accepts require additional reviewed evaluation. Unknown signs and neutral signs are unsupported. Re-run and re-document evaluation after any model, preprocessing, dataset or decision-policy change.

## Acceptance record

No production acceptance or reviewer signoff is recorded. Required next evidence includes signer-identified group separation or a clearly stated alternative, independent camera/crop evaluation, calibrated/rejection policy with negative examples, named-device latency/memory, runtime parity, and reviewer/date/signoff.
