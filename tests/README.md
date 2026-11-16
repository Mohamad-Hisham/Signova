# tests

Owner: **Hisham; producer/consumer owners supply acceptance evidence**.

Shared contract and multi-module integration acceptance specifications and safe fixture policy.

| Boundary | Responsibility |
|---|---|
| Receives | Central contracts and explicitly reviewed end-to-end requirements. |
| Produces | Future boundary/regression evidence distinct from module-local tests and model science. |
| Consumers and dependencies | All modules and final acceptance. |
| Never store here | Application tests executed in this scaffold, private user data or fake performance evidence. |

## Directory contents

| Entry | Purpose |
|---|---|
| [contracts/](contracts/README.md) | Future producer/consumer schema and version consistency scenarios. |
| [fixtures/](fixtures/README.md) | Shared safe fixture planning and future immutable permitted references. |
| [integration/](integration/README.md) | Future cross-module camera-to-preview-to-confirmed-text and failure acceptance. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
