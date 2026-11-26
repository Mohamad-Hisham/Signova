# docs

Owner: **Hisham; document-specific owners named inside**.

Shared architecture, contracts, team agreements, data policy and runbooks.

| Boundary | Responsibility |
|---|---|
| Receives | Current request, all six references and owner-reviewed decisions. |
| Produces | Implementation guidance, explicit interfaces and acceptance plans. |
| Consumers and dependencies | All frontend, backend, model and data owners. |
| Never store here | Executable application code, secret tokens, private transcripts or unapproved source media. |

## Directory contents

| Entry | Purpose |
|---|---|
| [architecture/](architecture/README.md) | System diagrams, runtime flow and the repository layout/file inventory. |
| [contracts/](contracts/README.md) | Central REST, WebSocket, adapter, data, vocabulary and UI behavior specifications. |
| [datasets/](datasets/README.md) | Candidate source links and engineering governance policy. |
| [Signova Backend Guide](guides/Signova-Backend-Guide.pdf) | Illustrated backend handover, local setup and integration plan. |
| [runbooks/](runbooks/README.md) | Continuous integration guidance and application integration acceptance. |
| [team/](team/README.md) | Ownership, receiver handoffs, Git workflow and meeting rhythm. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
