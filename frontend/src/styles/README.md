# frontend/src/styles

Owner: **Adham**.

Comment-only design-token and global layout/RTL/focus style plans.

| Boundary | Responsibility |
|---|---|
| Receives | Accessible reviewed layout and typography requirements. |
| Produces | Future consistent responsive Arabic/English presentation. |
| Consumers and dependencies | Application shell, reusable components and all feature surfaces. |
| Never store here | Executable scripts, actual sign media, reversed text hacks or CSS that mirrors transmitted bytes. |

## Directory contents

| Entry | Purpose |
|---|---|
| [global.css](global.css) | Reserve global responsive, RTL/LTR, focus and plain-text layout behavior. |
| [tokens.css](tokens.css) | Reserve consistent accessible visual tokens for Signova UI. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
