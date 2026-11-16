# ml/alphabet/configs

Owner: **Osama**.

Future training, deterministic preprocessing and rejection/capability recipe specifications.

| Boundary | Responsibility |
|---|---|
| Receives | Approved task, data/split versions and measured validation choices. |
| Produces | Future reproducible owner-specific recipes; currently Markdown guidance only. |
| Consumers and dependencies | dataset.py, train.py, predict.py, evaluate.py and release manifest. |
| Never store here | Fabricated feature dimensions, tutorial values presented as approved defaults, secrets or user payloads. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Configuration status

Actual architecture/hyperparameters, tensor shapes, class count, input/decision/calibration/neutral policy and runtime settings are TBD, not adopted from tutorial values. Describe planned schemas/units/version lineage here; create real configuration only after the task/input contract is approved. Train-only stochastic augmentation is separate from deterministic evaluation/runtime preprocessing. Never fit policy/normalization from final test data.
