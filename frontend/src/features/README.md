# frontend/src/features

Owner: **Adham**.

Product surfaces grouped by visible user purpose.

| Boundary | Responsibility |
|---|---|
| Receives | Controller state/actions, approved vocabulary/help and accessible screen requirements. |
| Produces | Future Homepage, recognition, transcript, library, recovery and help surfaces. |
| Consumers and dependencies | app/App.tsx and behavior-driven frontend/e2e tests. |
| Never store here | Independent cameras/sockets in each view, unsupported product features or model inference. |

## Directory contents

| Entry | Purpose |
|---|---|
| [about-help/](about-help/README.md) | About/Help scope, permissions, segmentation and privacy explanations. |
| [home/](home/README.md) | Homepage, mode/readiness/privacy entry. |
| [recognition/](recognition/README.md) | Live Translator, separate candidate preview and mode-specific controls. |
| [recovery/](recovery/README.md) | Explicit opt-in recovery record and offline/expired local-copy display. |
| [sign-library/](sign-library/README.md) | Searchable supported signs and approved examples. |
| [transcript/](transcript/README.md) | Confirmed transcript display, paused editor, explicit copy/download actions. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
