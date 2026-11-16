# frontend/src/features/home

Owner: **Adham**.

Homepage, mode/readiness/privacy entry.

| Boundary | Responsibility |
|---|---|
| Receives | Public catalogue/readiness and pre-creation recovery choice. |
| Produces | Future ready/unavailable mode cards and deliberate Continue intent. |
| Consumers and dependencies | Session controller, application shell and home acceptance tests. |
| Never store here | Automatic camera start, login/history links or hardcoded model capabilities. |

## Directory contents

| Entry | Purpose |
|---|---|
| [HomePage.tsx](HomePage.tsx) | Present Homepage mode selection, readiness and temporary-data/recovery choices. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
