# docs/runbooks

Owner: **Hisham coordinates; module owners maintain their operational instructions**.

Continuous integration guidance and application integration acceptance.

| Boundary | Responsibility |
|---|---|
| Receives | Actual scaffold structure and later owner-reviewed runtime/release evidence. |
| Produces | Honest current status and reproducible future acceptance procedures. |
| Consumers and dependencies | Every contributor and final integration/release reviewer. |
| Never store here | Working deployment scripts, false passing tests, fake environment locks or secret operational payloads. |

## Directory contents

| Entry | Purpose |
|---|---|
| [continuous-integration.md](continuous-integration.md) | CI behavior, local commands, hosted success/failure smoke tests and required-check setup. |
| [integration-checklist.md](integration-checklist.md) | Future cross-module acceptance matrix separating software correctness, scientific evidence and current scaffold status. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
