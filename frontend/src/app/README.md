# frontend/src/app

Owner: **Adham**.

Shell, serializable reducer and single resource-owning session controller.

| Boundary | Responsibility |
|---|---|
| Receives | Validated snapshots/events, explicit user actions and camera/network outcomes. |
| Produces | Future composed screens and coherent side effects/versioned state. |
| Consumers and dependencies | Feature views and frontend tests. |
| Never store here | Network side effects inside the reducer, multiple resource owners or previews appended as text. |

## Directory contents

| Entry | Purpose |
|---|---|
| [App.tsx](App.tsx) | Compose Homepage, Live Translator, Sign Library, About/Help and terminal/recovery surfaces. |
| [sessionController.ts](sessionController.ts) | Own a single session side-effect lifecycle across REST, socket and camera. |
| [sessionReducer.ts](sessionReducer.ts) | Define serializable browser state transitions without losing confirmed text or dirty drafts. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
