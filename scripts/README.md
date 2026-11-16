# scripts

Owner: **Hisham; relevant module owner reviews future helpers**.

Documentation-only cross-module helper extension point.

| Boundary | Responsibility |
|---|---|
| Receives | A concrete repeated local task with established module commands. |
| Produces | Future small wrappers for validation/integration after implementation exists. |
| Consumers and dependencies | All contributors and reproducibility workflow. |
| Never store here | Duplicate training/preprocessing logic, installers, download/deployment scripts or executable scaffold automation. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Helper policy

No executable helper is created by the scaffold. Future root helpers wrap established module commands only when a repeated cross-module task justifies them. Data operations remain in `data/scripts/`, training/export in owner packages, application logic in frontend/backend. Avoid a second copy of preprocessing, test orchestration invented before real tests, installers or deployment automation.
