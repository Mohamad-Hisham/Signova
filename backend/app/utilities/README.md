# backend/app/utilities

Owner: **Ali**.

Safe IDs, content-free errors and separate monotonic/UTC clock placeholders.

| Boundary | Responsibility |
|---|---|
| Receives | Validated operation context and operating-system clock/randomness when implemented. |
| Produces | Future unguessable identifiers, safe diagnostics and deterministic timer abstractions. |
| Consumers and dependencies | Session/command/recognition services and API/WS serialization. |
| Never store here | Raw payload logging, transcripts/frames, hidden persistence or capability values in errors. |

## Directory contents

| Entry | Purpose |
|---|---|
| [errors.py](errors.py) | Reserve safe uniform REST/WS failure construction and redaction conventions. |
| [ids.py](ids.py) | Reserve distinct opaque IDs, command UUID validation and cryptographically random session-secret helpers. |
| [time.py](time.py) | Reserve separate monotonic deadline/stability timing and UTC display timestamps. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
