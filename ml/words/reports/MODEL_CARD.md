# Signova word model card template

Owner: Bavly. Status: **unfilled template; no model trained, exported, measured or released by this scaffold.** A future accepted card must refer to an actual immutable artifact and evaluated scope. All model facts below remain TBD.

| Required section | Evidence to supply |
|---|---|
| Identity and intended use | Model ID/version/hash, approved sign variety, exact supported labels/variants, intended users and excluded conditions |
| Architecture/input/output | Actual representation, shapes/axes/dtype, feature/extractor version, class order, score semantics and runtime/provider |
| Data and provenance | Dataset/split/label/annotation/recipe versions, rights/use limits, pretrained provenance, independent signer/group support and test exposure |
| Preprocessing and decision policy | Orientation/handedness, crop/pad/color/scaling, missing context, fitted parameters, calibration/rejection/neutral capability and policy version |
| Recognition evidence | Per-class support/accuracy/precision/recall/macro metrics, confusion cases, accepted accuracy plus coverage and defined negative false accepts |
| Live capability | Complete isolated clips versus rolling windows, timestamps/length/masks/gap/reset needs; boundary/neutral evidence; manual versus automatic event results and hold/repeat failures |
| Performance | Named CPU/GPU/OS/runtime, load/warmup, decode/extract/preprocess/infer/window delay, p50/p95, memory and concurrency |
| Integration | First inference, golden fixture permissions/tolerances, backend compatibility/reset/parity and safe error/unavailable behavior |
| Limitations and maintenance | Weak classes/conditions, residual false accepts, controlled collection needs, version/rollback and withdrawal impact |
| Acceptance record | Actual evidence references, receiver/reviewer/date, Hisham accepted scope and unresolved risks; no fabricated signoff |

A model score is not calibrated accuracy. Unit tests and one successful webcam example do not establish independent recognition performance. Do not store restricted media, participant identities, user transcripts or private prediction tables in this tracked card. Link approved aggregate evidence and controlled references instead.
