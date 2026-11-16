# ml/words

Owner: **Bavly**.

isolated Arabic word model package source/config/test/report scaffold.

| Boundary | Responsibility |
|---|---|
| Receives | Basil approved task data plus owner-reviewed representation and runtime requirements. |
| Produces | Future independent trained/evaluated predictor and immutable release. |
| Consumers and dependencies | Ali dedicated adapter and artifacts/words/. |
| Never store here | Backend route logic, transcript mutation, other model maps or restricted data/weights in ordinary Git. |

## Directory contents

| Entry | Purpose |
|---|---|
| [configs/](configs/README.md) | Future training, deterministic preprocessing and rejection/capability recipe specifications. |
| [reports/](reports/README.md) | Model card template and future safe scientific/benchmark summaries. |
| [src/](src/README.md) | Comment-only dataset, model, training, evaluation, prediction, export, preprocessing and decision modules. |
| [tests/](tests/README.md) | Future loader, preprocessing, rejection, golden, parity and mode-specific acceptance. |
| [requirements.in](requirements.in) | Reserve direct dependency intent for word model development. |
| [requirements.lock.txt](requirements.lock.txt) | Reserve a tested dependency lock for word reproducibility. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Owner-specific implementation boundary

Bavly owns this model's task formulation, data acceptance requirements, architecture/training/evaluation, deterministic preprocessing, rejection/calibration, side-effect-free inference and immutable release evidence. Basil supplies approved data; Ali wraps the package; Adham consumes public candidates/snapshots. Neither model writes transcripts. Exact word sequence/capability/neutral evidence must fit the live JPEG window; manual Confirm does not make a clip-only model compatible.

All eight source modules and both requirement files contain comments only. `dataset.py`/`preprocessing.py` prepare agreed inputs, `model.py` defines architecture, `train.py` is offline work, `evaluate.py` measures frozen evidence, `predict.py` calls architecture/recipe/decision without importing training, `decision.py` supplies recognition policy, and `export.py` optionally produces a tested runtime artifact. No model, training, inference, neutral detector, export or actual lock exists yet. Packaging/build metadata and exact dependencies remain future owner decisions.

Read `../../docs/contracts/model-interface.md`, `../../docs/contracts/dataset-contract.md`, and `../../artifacts/words/RELEASE-TEMPLATE.md`. Track only safe reports/model cards/config specifications; large weights/restricted data live outside ordinary Git. Each future release is accepted on golden/parity, task-specific scientific evidence and named runtime hardware, never a tutorial score.
