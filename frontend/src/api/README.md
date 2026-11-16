# frontend/src/api

Owner: **Adham with Ali contract review**.

Native Fetch client, runtime validation and single WebSocket transport placeholders.

| Boundary | Responsibility |
|---|---|
| Receives | Exact /api/v1 REST/WS fields, capabilities in controller memory and command identities. |
| Produces | Future validated responses/events and safe request failures. |
| Consumers and dependencies | app/sessionController.ts, camera/frameSampler.ts and browser contract tests. |
| Never store here | Alternative routes, Socket.IO/Axios dependencies, token URLs, raw payload logging or model imports. |

## Directory contents

| Entry | Purpose |
|---|---|
| [client.ts](client.ts) | Provide the future native Fetch boundary for the exact REST v1 catalogue. |
| [contracts.ts](contracts.ts) | Mirror approved public REST/WS types and selected Zod runtime validation. |
| [liveSocket.ts](liveSocket.ts) | Own the future native WebSocket transport lifecycle and v1 envelope dispatch. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
