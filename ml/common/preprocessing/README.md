# ml/common/preprocessing

Owner: **Osama and Bavly jointly**.

Reserved common deterministic-operation documentation.

| Boundary | Responsibility |
|---|---|
| Receives | A proven identical transformation accepted by both model owners. |
| Produces | Future small reusable transform behavior with matched fixtures. |
| Consumers and dependencies | Owner-local preprocessing modules, only if behavior matches. |
| Never store here | Forced common crop, feature count, handedness or sampling policy. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Reuse gate

Each owner starts with `ml/<task>/src/preprocessing.py`. Move a utility here only if both owners show identical semantics and matching golden inputs/outputs. Sharing a file path must never force common crop/handedness, tensor dimensions, temporal sampling or missing-feature encoding. No common transform is implemented in this delivery.
