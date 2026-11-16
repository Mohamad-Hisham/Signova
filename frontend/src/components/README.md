# frontend/src/components

Owner: **Adham**.

Reusable accessible status and confirmation-dialog placeholders.

| Boundary | Responsibility |
|---|---|
| Receives | Reviewed labels, safe status codes and controlled open/close/actions. |
| Produces | Future semantic shared controls with predictable focus and feedback. |
| Consumers and dependencies | Home, recognition, transcript, help and recovery features. |
| Never store here | Feature-specific network/camera owners, private debug payloads or raw HTML rendering. |

## Directory contents

| Entry | Purpose |
|---|---|
| [ConfirmDialog.tsx](ConfirmDialog.tsx) | Provide accessible deliberate confirmation for meaningful removal/navigation actions. |
| [StatusMessage.tsx](StatusMessage.tsx) | Present reusable safe status and error guidance without noisy private diagnostics. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
