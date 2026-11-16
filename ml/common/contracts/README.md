# ml/common/contracts

Owner: **Osama and Bavly jointly**.

Shared evidence/manifest meaning documentation.

| Boundary | Responsibility |
|---|---|
| Receives | Ali adapter contract and both owners input/output semantics. |
| Produces | Future common validation conventions without model-specific shape assumptions. |
| Consumers and dependencies | Both model packages and backend adapter review. |
| Never store here | Competing REST/WS schemas, fixed tensors or silently merged word/alphabet IDs. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Boundary authority

`../../../docs/contracts/model-interface.md` owns common adapter evidence meaning. Task-specific shapes, class maps, score scales, neutral capabilities and runtime interfaces stay owner-specific. Any reusable validation must preserve those distinctions and follow the accepted null-score translation decision. No Python/types/schema implementation is supplied.
