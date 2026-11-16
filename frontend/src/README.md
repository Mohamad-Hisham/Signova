# frontend/src

Owner: **Adham**.

Comment-only application, network, camera, features, shared UI, style and mock planning files.

| Boundary | Responsibility |
|---|---|
| Receives | Public contracts and screen/retention requirements. |
| Produces | Future browser-only UI and one session controller; currently no runnable code. |
| Consumers and dependencies | frontend/tests/, frontend/e2e/ and backend integration acceptance. |
| Never store here | Model runtimes, data archives, hidden transcript stores or credentials in source. |

## Directory contents

| Entry | Purpose |
|---|---|
| [api/](api/README.md) | Native Fetch client, runtime validation and single WebSocket transport placeholders. |
| [app/](app/README.md) | Shell, serializable reducer and single resource-owning session controller. |
| [camera/](camera/README.md) | Permission/track ownership and bounded unmirrored JPEG sampling placeholders. |
| [components/](components/README.md) | Reusable accessible status and confirmation-dialog placeholders. |
| [features/](features/README.md) | Product surfaces grouped by visible user purpose. |
| [mocks/](mocks/README.md) | Development-only synthetic transport scenario descriptions; no fake runtime yet. |
| [styles/](styles/README.md) | Comment-only design-token and global layout/RTL/focus style plans. |
| [main.tsx](main.tsx) | Future browser entrypoint and React root ownership. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
