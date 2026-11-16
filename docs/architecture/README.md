# docs/architecture

Owner: **Hisham**.

System diagrams, runtime flow and the repository layout/file inventory.

| Boundary | Responsibility |
|---|---|
| Receives | Reviewed handbooks, board geometry/images and current project constraints. |
| Produces | Dependency boundaries, original-file preservation evidence and complete tree. |
| Consumers and dependencies | All modules, integration QA and new teammates. |
| Never store here | Invented capabilities, unverified performance claims or deployable infrastructure. |

## Directory contents

| Entry | Purpose |
|---|---|
| [monorepo-structure.md](monorepo-structure.md) | Directory dependency rules and every meaningful deviation from the requested/handbook layouts. |
| [runtime-data-flow.md](runtime-data-flow.md) | Live sampling, REST/WebSocket sequence, candidate/commit distinction and transcript lifecycle diagrams. |
| [system-overview.md](system-overview.md) | System context, modular monorepo components, model integration and scope boundaries with diagrams. |
| [file-catalog.md](file-catalog.md) | Complete per-file owner, purpose and placeholder/original status inventory. |
| [repository-tree.md](repository-tree.md) | Complete project file tree including all original references and new scaffold files. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
