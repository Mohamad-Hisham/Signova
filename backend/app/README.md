# backend/app

Owner: **Ali**.

Comment-only app startup/settings, schemas, REST/WS boundaries, services, adapters and utilities.

| Boundary | Responsibility |
|---|---|
| Receives | Exact contracts, trusted artifact locations and reviewed runtime policy. |
| Produces | Future one-process FastAPI runtime with bounded in-memory session authority. |
| Consumers and dependencies | Frontend contracts and backend tests. |
| Never store here | Business logic in import-time configuration, user data on disk or model training. |

## Directory contents

| Entry | Purpose |
|---|---|
| [api/](api/README.md) | REST-only health/catalogue/session/transcript boundary placeholders. |
| [models/](models/README.md) | Common adapter boundary and independent alphabet/word/development-fake placeholders. |
| [schemas/](schemas/README.md) | Common response, REST request and WebSocket event placeholder schemas. |
| [services/](services/README.md) | RAM/session, recognition, transcript, word-gate and command coordination placeholders. |
| [utilities/](utilities/README.md) | Safe IDs, content-free errors and separate monotonic/UTC clock placeholders. |
| [ws/](ws/README.md) | Single v1 live-session WebSocket boundary placeholder. |
| [config.py](config.py) | Reserve typed runtime settings and validated startup policy. |
| [main.py](main.py) | Reserve the one FastAPI application composition and lifecycle boundary. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
