# backend/app/schemas

Owner: **Ali with Adham consumer review**.

Common response, REST request and WebSocket event placeholder schemas.

| Boundary | Responsibility |
|---|---|
| Receives | Published field names/types/constraints and documented unresolved decisions. |
| Produces | Future Pydantic v2 validated wire objects with safe serialization. |
| Consumers and dependencies | REST/WS handlers, services and frontend runtime schema alignment. |
| Never store here | Unannounced fields, filesystem paths, rejected private values or model frameworks. |

## Directory contents

| Entry | Purpose |
|---|---|
| [common.py](common.py) | Reserve canonical Session, Transcript, Item, Candidate and safe Error response shapes. |
| [events.py](events.py) | Reserve all protocol v1 client messages, server envelopes and event data objects. |
| [rest.py](rest.py) | Reserve strict REST creation, capture, confirm, space, replacement, clear and end input schemas. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
