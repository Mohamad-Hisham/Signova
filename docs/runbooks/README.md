# docs/runbooks

Owner: **Hisham coordinates; module owners maintain their operational instructions**.

Scaffold verification and future setup, model promotion and integration acceptance.

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
| [local-development.md](local-development.md) | Honest non-runnable scaffold status and owner-led future environment/integration prerequisites. |
| [model-release.md](model-release.md) | Complete versioned model promotion, fresh-runtime parity, live acceptance and coordinated rollback process. |
| [scaffold-verification.md](scaffold-verification.md) | Static scaffold audit results, original-file preservation and strict implementation-boundary confirmation. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
