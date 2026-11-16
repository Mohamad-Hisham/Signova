# tests

Owner: **Hisham; producer/consumer owners supply acceptance evidence**.

Shared acceptance specifications, CI-tooling regression tests and safe fixture policy.

| Boundary | Responsibility |
|---|---|
| Receives | Central contracts, synthetic CI cases and reviewed end-to-end requirements. |
| Produces | CI-tooling regression evidence and future application acceptance plans. |
| Consumers and dependencies | All modules and final acceptance. |
| Never store here | Private user data, model binaries or fake performance evidence. |

## Directory contents

| Entry | Purpose |
|---|---|
| [ci/](ci/README.md) | Implemented repository-checker tests with no application imports. |
| [contracts/](contracts/README.md) | Future producer/consumer schema and version consistency scenarios. |
| [fixtures/](fixtures/README.md) | Shared safe fixture planning and future immutable permitted references. |
| [integration/](integration/README.md) | Future cross-module camera-to-preview-to-confirmed-text and failure acceptance. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

Only `ci/` is executable today. Application contract/integration suites remain planned;
passing checker tests does not demonstrate API, UI or model correctness.
