# backend/tests

Owner: **Ali**.

Future unit/API/WS/model-parity acceptance descriptions.

| Boundary | Responsibility |
|---|---|
| Receives | Synthetic clocks/predictions, strict contracts and later permitted fixtures. |
| Produces | Future deterministic runtime behavior evidence, separate from model quality. |
| Consumers and dependencies | Backend reviews and shared integration QA. |
| Never store here | Executed tests in this scaffold, private session data or dependency installations. |

## Directory contents

| Entry | Purpose |
|---|---|
| [fixtures/](fixtures/README.md) | Safe future synthetic request/event descriptions and approved tiny golden references. |
| [integration/](integration/README.md) | Future REST/WS/access/startup/adapter interaction acceptance. |
| [unit/](unit/README.md) | Future isolated command/session/transcript/gate/validation acceptance. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
