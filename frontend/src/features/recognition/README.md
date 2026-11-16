# frontend/src/features/recognition

Owner: **Adham**.

Live Translator, separate candidate preview and mode-specific controls.

| Boundary | Responsibility |
|---|---|
| Receives | Current stream/candidate, capture status, confirmed snapshot and permitted policy. |
| Produces | Future accessible camera/preview workspace and explicit confirmation intentions. |
| Consumers and dependencies | Controller, transcript surfaces and live browser acceptance. |
| Never store here | Appending candidate text locally, fake detection overlays or scientific threshold sliders. |

## Directory contents

| Entry | Purpose |
|---|---|
| [RecognitionPreview.tsx](RecognitionPreview.tsx) | Display only current candidate evidence and Confirm eligibility. |
| [RecognitionWorkspace.tsx](RecognitionWorkspace.tsx) | Compose Live Translator camera, candidate, confirmed transcript and session controls. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
