# ml/alphabet/src

Owner: **Osama**.

Comment-only dataset, model, training, evaluation, prediction, export, preprocessing and decision modules.

| Boundary | Responsibility |
|---|---|
| Receives | Frozen dataset/mapping/recipe plus explicitly assigned future implementation. |
| Produces | Future scientific pipeline and side-effect-free inference package. |
| Consumers and dependencies | Owner tests/reports, artifact release and Ali adapter. |
| Never store here | Inference imports of training entrypoints, transcript writes, live collection or model binaries. |

## Directory contents

| Entry | Purpose |
|---|---|
| [dataset.py](dataset.py) | Reserve the alphabet model-specific loader for Basil approved immutable releases. |
| [decision.py](decision.py) | Reserve the alphabet classifier rejection/calibration and neutral-capability policy. |
| [evaluate.py](evaluate.py) | Reserve alphabet scientific evaluation, rejection coverage and target-runtime benchmarks. |
| [export.py](export.py) | Reserve optional alphabet inference export and complete versioned package assembly. |
| [model.py](model.py) | Reserve the independent alphabet model architecture definition used by training and inference. |
| [predict.py](predict.py) | Reserve side-effect-free alphabet inference from a trusted frozen release. |
| [preprocessing.py](preprocessing.py) | Reserve the exact deterministic alphabet training-evaluation-serving input recipe. |
| [train.py](train.py) | Reserve offline alphabet training and controlled validation checkpoint selection. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
