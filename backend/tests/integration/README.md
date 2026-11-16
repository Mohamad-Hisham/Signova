# backend/tests/integration

Owner: **Ali**.

Future REST/WS/access/startup/adapter interaction acceptance.

| Boundary | Responsibility |
|---|---|
| Receives | Actual future app lifespan with controlled adapters and permitted fixtures. |
| Produces | Future exact status/event ordering, access, cancellation and parity evidence. |
| Consumers and dependencies | Frontend integration and model release acceptance. |
| Never store here | Real secrets, restricted recordings or silently skipped readiness failures. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Future route/socket/runtime cases

Use a future application lifespan context with explicit development adapters; create isolated sessions, authenticate, start, send valid tiny samples and assert both REST responses and socket events. Exercise every route's access/validation/expiry, each mutation's key/version/concurrency, one-socket/Origin/close semantics, startup checksum failure, per-stream state isolation and late work after removal. No app or tests exist yet.
