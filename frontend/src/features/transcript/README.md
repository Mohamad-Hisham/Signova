# frontend/src/features/transcript

Owner: **Adham**.

Confirmed transcript display, paused editor, explicit copy/download actions.

| Boundary | Responsibility |
|---|---|
| Receives | Canonical transcript items/text/revision, separate user draft and command outcomes. |
| Produces | Future editable drafts, replacement intents and user-controlled copies. |
| Consumers and dependencies | Controller, REST client, recovery removal and transcript tests. |
| Never store here | Model provenance on changed text, permanent history, automatic training labels or hidden persistence. |

## Directory contents

| Entry | Purpose |
|---|---|
| [TranscriptEditor.tsx](TranscriptEditor.tsx) | Edit a separate paused transcript draft using the base server revision. |
| [TranscriptPanel.tsx](TranscriptPanel.tsx) | Render canonical confirmed transcript and available text actions. |
| [transcriptActions.ts](transcriptActions.ts) | Own explicit browser clipboard and local/authorized-server TXT download interactions. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
