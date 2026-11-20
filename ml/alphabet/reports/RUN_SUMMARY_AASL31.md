# AASL31 full-frame baseline run summary

## Provenance

- Experiment ID: `aasl31_full_frame_baseline_v1`
- Training reference: `Untitled13.ipynb` (SHA-256: `1d9ac118cba4ff6e6cef68df0ccd62fc40d77a221e341edac25d14d5ff0e3281`)
- Dataset: `muhammadalbrham/rgb-arabic-alphabets-sign-language-dataset`, retrieved with KaggleHub; 7,856 RGB images, 31 classes; Kaggle listing identifies CC BY-SA 4.0.
- Split: grouped by filename numeric suffix, `random_state=42`; 5,456 train / 1,173 validation / 1,227 test; no numeric-group overlap. Numeric group is not verified to mean signer identity.
- Model artifact: `checkpoints/aasl31_best.pth` (SHA-256: `5bc685f101ac1824130cec43af76ccc62f848572b94924cec617b101d31e5e5f`)
- Class mapping: `checkpoints/class_to_idx.json`
- Training hardware: Colab Tesla T4.

## Recipe

The original executed code is in the referenced notebook. `src/` now contains a code refactor of those steps; that refactor has not been run to reproduce this historical result.

MobileNetV3-Small with torchvision default pretrained weights; 31 output classes. RGB images resized to 224×224, converted to tensors, and normalized with ImageNet mean `(0.485, 0.456, 0.406)` and standard deviation `(0.229, 0.224, 0.225)`. Training used 12 epochs, batch size 32, AdamW (`lr=1e-4`), class-weighted cross entropy, and train-only random rotation (±8°) plus brightness/contrast jitter (0.15). The best checkpoint was selected by validation Macro-F1.

## Results

- Best checkpoint: epoch 11; validation Macro-F1 **0.9336**.
- Test accuracy **0.9324**.
- Test balanced accuracy **0.9307**.
- Test Macro-F1 **0.9300**.
- Test support: 1,227 images across 31 labels.

Per-class metrics, confusion counts, training history and figures are stored under `evidence/aasl31_full_frame_baseline_v1/`. The manifest is retained for split lineage; the dataset images themselves are not copied.

## Scope and caveats

This is a static image-classification result, not a validated live recognition result. Group-disjoint evaluation does not prove signer independence. A validation-only threshold search recorded score cutoff 0.89, margin cutoff 0.00, observed accepted precision 0.9802 on 1,009/1,173 images (coverage 0.86); the same validation split was used for model selection, so this is exploratory and not a calibrated or independently verified rejection policy. The hand-crop webcam experiment is separate and has not been evaluated against a new held-out crop test set.

The webcam script's `MIN_SCORE`, `MIN_MARGIN` and frame-vote settings are implementation heuristics, not calibrated confidence thresholds. No latency, memory, cross-device parity, unknown-sign, neutral-sign, temporal letter or word-recognition claim is made.
