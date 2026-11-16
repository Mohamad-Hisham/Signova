# data/configs

Owner: **Basil**.

Future separate alphabet/word preparation and split-rule specifications.

| Boundary | Responsibility |
|---|---|
| Receives | Owner-approved recipes, grouping objective and tested tool versions. |
| Produces | Future reproducible data preparation metadata aligned with each model. |
| Consumers and dependencies | Offline scripts, model loaders and runtime parity review. |
| Never store here | Guessed universal shapes, fitted test statistics, secrets or model experiment logic. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Future recipe fields

Specify separate alphabet and word representation/dtype/axes, orientation/context/crop/pad/color/scaling, extractor/version/feature order when applicable, timestamp rate/window/stride/missing/padding/gap/reset semantics, fitted-train-only values and split grouping objective/seed. All actual dimensions, rates and selected tools remain TBD per owner. Future JSON/YAML schemas are documented in Markdown until real implementation; no example config masquerades as an accepted recipe.
