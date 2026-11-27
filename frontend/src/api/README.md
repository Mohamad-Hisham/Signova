# frontend/src/api

Owner: **Adham with Ali contract review**.

Native Fetch client, runtime validation and single WebSocket transport.

| Boundary | Responsibility |
|---|---|
| Receives | Exact /api/v1 REST/WS fields, capabilities in controller memory and command identities. |
| Produces | Validated responses/events and safe request failures. |
| Consumers and dependencies | app/sessionController.ts, camera/frameSampler.ts and browser contract tests. |
| Never store here | Alternative routes, Socket.IO/Axios dependencies, token URLs, raw payload logging or model imports. |

## Directory contents

| Entry | Purpose |
|---|---|
| [client.ts](client.ts) | Use the native Fetch boundary for catalogues, sessions, transcript actions and downloads. |
| [contracts.ts](contracts.ts) | Mirror REST/WS schemas and validate network responses/events with Zod. |
| [liveSocket.ts](liveSocket.ts) | Authenticate the native WebSocket and validate v1 envelopes before dispatch. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
