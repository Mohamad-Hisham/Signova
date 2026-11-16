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
| [architecture/](architecture/README.md) | System diagrams, runtime flow, layout/file inventory and source review. |
| [contracts/](contracts/README.md) | Central REST, WebSocket, adapter, data, vocabulary and UI behavior specifications. |
| [datasets/](datasets/README.md) | Candidate source links and engineering governance policy. |
| [runbooks/](runbooks/README.md) | Scaffold verification and future setup, model promotion and integration acceptance. |
| [team/](team/README.md) | Ownership, receiver handoffs, Git workflow and meeting rhythm. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
