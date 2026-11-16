# tests/integration

Owner: **Hisham with Ali/Adham and model owners**.

Future cross-module camera-to-preview-to-confirmed-text and failure acceptance.

| Boundary | Responsibility |
|---|---|
| Receives | Controlled synthetic flows and later authorized real-model golden cases. |
| Produces | Future end-to-end hold/repeat/edit/removal/recovery/runtime evidence. |
| Consumers and dependencies | Release acceptance and cross-owner defect triage. |
| Never store here | Executed browser/model tests here, user recordings or claims that UI success proves accuracy. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Future full-path acceptance

Trace an authorized sample through browser JPEG, actual server decode, owner recipe, dedicated adapter, preview, Confirm, one RAM commit and one rendered snapshot. Reproduce hold/repeat, explicit Space, paused edits, conflicting/lost requests, Clear during work, offline removal, recovery consent, restart and model unavailability. Use named versions/hardware/browser and first-divergence diagnosis; consult `../../docs/runbooks/integration-checklist.md`. No app tests are executed now.
