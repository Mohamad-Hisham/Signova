# backend

Owners: **Hisham and Ali**.

One Python/FastAPI application scaffold, dependency notes and future test plans.

| Boundary | Responsibility |
|---|---|
| Receives | Browser contracts, approved inference packages and deployment compatibility requirements. |
| Produces | Future validated candidates and authoritative temporary session/transcript snapshots. |
| Consumers and dependencies | frontend/, model runtime acceptance and shared tests/. |
| Never store here | Training runs, database/Redis/accounts/history infrastructure or unreviewed model binaries. |

## Directory contents

| Entry | Purpose |
|---|---|
| [app/](app/README.md) | Comment-only app startup/settings, schemas, REST/WS boundaries, services, adapters and utilities. |
| [tests/](tests/README.md) | Future unit/API/WS/model-parity acceptance descriptions. |
| [.env.example](.env.example) | Describe future server-only runtime settings without active assignments or secrets. |
| [requirements.in](requirements.in) | Reserve direct dependency intent for the single backend runtime. |
| [requirements.lock.txt](requirements.lock.txt) | Reserve a tested dependency lock for the single backend runtime. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Current status and future stack

Every Python file is comments only; there is no FastAPI app, route, schema class, WebSocket handler, fake model or test implementation. Both requirement files contain explanatory comments, not installable/tested package pins. `.env.example` has no active assignments or secrets.

The initial compatibility target is Python 3.11 with FastAPI, Pydantic v2, Uvicorn, NumPy, Pillow, Pytest, HTTPX and Ruff; typed settings tooling and actual inference dependencies require a tested compatible selection. Both real model runtimes must coexist in one process. Optional OpenCV/MediaPipe follows the owner-approved model recipe only. Ali owns the REST and WebSocket contracts. Hisham owns the live frame pipeline, recognition services and adapter implementation. Both maintain the backend runtime, keeping training out of handlers and inference outside session locks and network loops.

Temporary per-session capabilities protect access without introducing accounts/auth infrastructure. One process/worker/replica is required; reload/restart loses RAM sessions. Real runtime configuration, exact package versions and run/test commands are future implementation deliverables. Read `../docs/contracts/rest-api.md`, `websocket-protocol.md` and `model-interface.md` in that contracts directory first.
