# backend/app/ws

Owner: **Basel**.

Single v1 live-session WebSocket boundary placeholder.

| Boundary | Responsibility |
|---|---|
| Receives | Origin, first auth, protocol frames/pings and service notifications. |
| Produces | Future serialized safe events and processed/discarded acknowledgements. |
| Consumers and dependencies | Browser live socket, recognition/session services and protocol tests. |
| Never store here | Direct transcript commands over WS, binary v1, recording queues or blocking inference in reader. |

## Directory contents

| Entry | Purpose |
|---|---|
| [live.py](live.py) | Reserve the single authenticated /api/v1/ws/sessions/{sid} connection boundary. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
