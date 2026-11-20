# ml/alphabet/reports

Owner: **Osama**.

This directory holds the model card and the evidence summary for the executed AASL31 full-frame baseline. Evidence files are aggregate metrics, training history, confusion counts/plots and split lineage; raw image data and contact sheets are not stored here.

| Entry | Purpose |
|---|---|
| [MODEL_CARD.md](MODEL_CARD.md) | Scope, training/evaluation results, limitations and outstanding acceptance evidence. |
| [RUN_SUMMARY_AASL31.md](RUN_SUMMARY_AASL31.md) | Run provenance and measured results. |
| `evidence/aasl31_full_frame_baseline_v1/` | Aggregate outputs copied from the local Colab export. |
| `archive/MODEL_CARD.unfilled-template.md` | Preserved original scaffold template. |

The test scores describe the frozen full-frame image classifier on the recorded test partition. They do not establish independent signer, webcam-crop, continuous signing, or deployment performance. The validation threshold experiment is not calibrated and must not be represented as test accuracy.
