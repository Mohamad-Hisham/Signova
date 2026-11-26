# backend/app/api

Owner: **Hisham**.

REST-only health/catalogue/session/transcript boundary placeholders.

| Boundary | Responsibility |
|---|---|
| Receives | Validated requests, bearer capabilities and service outcomes. |
| Produces | Future documented status codes and canonical response snapshots. |
| Consumers and dependencies | Frontend Fetch client, schemas and backend integration tests. |
| Never store here | Model training, duplicate session stores, inference loops or alternative REST routes. |

## Directory contents

| Entry | Purpose |
|---|---|
| [catalog.py](catalog.py) | Reserve public /api/v1/models and /api/v1/vocabulary REST boundaries. |
| [health.py](health.py) | Reserve public /api/v1/health/live and /health/ready REST boundaries. |
| [sessions.py](sessions.py) | Reserve REST create/read/capture/confirm/space/end/delete session boundaries. |
| [transcript.py](transcript.py) | Reserve replacement, clear and current-revision TXT export REST boundaries. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
