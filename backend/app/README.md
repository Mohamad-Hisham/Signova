# backend/app

Owners: **Hisham and Ali**.

FastAPI startup, REST and WebSocket handlers, request and response schemas, session services, and model adapters. [Run the backend](../README.md)

| Boundary | Responsibility |
|---|---|
| Receives | Exact contracts, trusted artifact locations and reviewed runtime policy. |
| Produces | A one-process FastAPI runtime with bounded in-memory sessions. |
| Consumers and dependencies | Frontend contracts and backend tests. |
| Never store here | Business logic in import-time configuration, user data on disk or model training. |

## Directory contents

| Entry | Purpose |
|---|---|
| [api/](api/README.md) | Health, catalogues, sessions, and transcript REST handlers. |
| [models/](models/README.md) | Common adapter interface and the AASL31 alphabet runtime. |
| [schemas/](schemas/README.md) | REST request and response schemas and WebSocket message schemas. |
| [services/](services/README.md) | In-memory sessions, recognition, transcript mutations, and command coordination. |
| [utilities/](utilities/README.md) | IDs, safe errors, and clocks. |
| [ws/](ws/README.md) | Authenticated v1 WebSocket for live sessions. |
| [config.py](config.py) | Settings, model paths, and runtime limits. |
| [main.py](main.py) | Route composition and startup and shutdown lifecycle. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
