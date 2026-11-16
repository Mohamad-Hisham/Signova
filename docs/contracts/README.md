# docs/contracts

Owner: **Ali coordinates runtime contracts; Basil dataset/vocabulary; model owners their semantics; Adham browser review**.

Central REST, WebSocket, adapter, data, vocabulary and UI behavior specifications.

| Boundary | Responsibility |
|---|---|
| Receives | Detailed handbooks and explicit shared decisions. |
| Produces | One reviewable source per interface, with fields/errors/version behavior. |
| Consumers and dependencies | frontend/, backend/, ml/, data/ and shared tests/. |
| Never store here | Alternative silent routes/fields, fake JSON manifests, weights or private example payloads. |

## Directory contents

| Entry | Purpose |
|---|---|
| [dataset-contract.md](dataset-contract.md) | Manifest/annotation fields, rights, independent splits, model-specific recipes and usable offline release handoffs. |
| [frontend-backend-contract.md](frontend-backend-contract.md) | Screen/control duties, authority, version merging, camera cleanup, recovery and exact user-visible failure behavior. |
| [model-interface.md](model-interface.md) | Separate model representations, common adapter evidence, release deliverables and scientific/runtime acceptance. |
| [rest-api.md](rest-api.md) | Exact REST routes, fields, access, status codes, mutation semantics, retries and failures from both handbooks. |
| [starting-limits.md](starting-limits.md) | Explicitly label all handbook limits and targets as initial settings requiring model and hardware verification. |
| [vocabulary-contract.md](vocabulary-contract.md) | Stable semantic IDs, Arabic/public field mappings, class order and unresolved approved English distribution. |
| [websocket-protocol.md](websocket-protocol.md) | Exact WebSocket URL, handshake, envelopes, all client/server message fields and flow-control/close semantics. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
