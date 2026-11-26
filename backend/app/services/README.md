# backend/app/services

Owner: **Hisham**.

RAM/session, recognition, transcript, word-gate and command coordination placeholders.

| Boundary | Responsibility |
|---|---|
| Receives | Validated handlers, approved adapter evidence, user commands and server clock. |
| Produces | Future atomic session changes, candidate gating and canonical transcript snapshots. |
| Consumers and dependencies | REST/WS layers, model adapters and focused unit/integration tests. |
| Never store here | Database calls, automatic grammar, network delivery awaited under locks or model training. |

## Directory contents

| Entry | Purpose |
|---|---|
| [commands.py](commands.py) | Reserve shared revision/state-version and bounded idempotency coordination. |
| [recognition.py](recognition.py) | Reserve bounded sample admission, model routing and current candidate/segment orchestration. |
| [sessions.py](sessions.py) | Reserve authoritative temporary RAM session and capability lifecycle. |
| [transcript.py](transcript.py) | Reserve authoritative temporary confirmed transcript validation and atomic snapshots. |
| [word_gate.py](word_gate.py) | Reserve deterministic word stability, evaluated release and segment-latch state transitions. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
