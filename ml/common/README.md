# ml/common

Owner: **Osama and Bavly jointly; Hisham coordinates**.

Documentation-only shared contract, preprocessing and evaluation extension points.

| Boundary | Responsibility |
|---|---|
| Receives | Demonstrated identical semantics agreed by both model owners. |
| Produces | Future narrowly reused utilities only after duplication/semantics justify them. |
| Consumers and dependencies | Independent model packages and compatibility checks. |
| Never store here | Premature shared dimensions, unified label maps, common normalization assumptions or cross-session state. |

## Directory contents

| Entry | Purpose |
|---|---|
| [contracts/](contracts/README.md) | Shared evidence/manifest meaning documentation. |
| [evaluation/](evaluation/README.md) | Reserved common metric/report convention documentation. |
| [preprocessing/](preprocessing/README.md) | Reserved common deterministic-operation documentation. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
