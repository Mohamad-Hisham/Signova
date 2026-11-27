# frontend/src/app

Owner: **Adham**.

Shell, serializable reducer and single session controller.

| Boundary | Responsibility |
|---|---|
| Receives | Validated snapshots/events, explicit user actions and camera/network outcomes. |
| Produces | Composed screens and coherent side effects/versioned state. |
| Consumers and dependencies | Feature views and frontend tests. |
| Never store here | Network side effects inside the reducer, multiple resource owners or previews appended as text. |

## Directory contents

| Entry | Purpose |
|---|---|
| [App.tsx](App.tsx) | Route the landing page and Word/Alphabet translator workspaces. |
| [sessionController.ts](sessionController.ts) | Coordinate REST, socket, camera and transcript actions for one translator route. |
| [sessionReducer.ts](sessionReducer.ts) | Merge serializable state, independent snapshot versions, candidates and editor drafts. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
