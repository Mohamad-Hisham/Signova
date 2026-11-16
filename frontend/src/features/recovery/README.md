# frontend/src/features/recovery

Owner: **Adham**.

Explicit opt-in recovery record and offline/expired local-copy display.

| Boundary | Responsibility |
|---|---|
| Receives | Consent, confirmed snapshot, limited credential metadata, expiry and server outcome. |
| Produces | Future bounded tab recovery or honestly labeled local copy/removal intent. |
| Consumers and dependencies | Controller, transcript actions and browser recovery tests. |
| Never store here | Default persistence, localStorage/IndexedDB history, camera samples, candidates or unsaved drafts in storage. |

## Directory contents

| Entry | Purpose |
|---|---|
| [RecoveryView.tsx](RecoveryView.tsx) | Explain reconnection, expiry and recovered local copy without claiming active server state. |
| [recoveryStore.ts](recoveryStore.ts) | Manage explicitly opted-in bounded tab recovery without restoring removed content. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
