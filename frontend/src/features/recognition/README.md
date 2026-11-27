# frontend/src/features/recognition

Owner: **Adham**.

Shared Word and Alphabet translator workspaces with separate candidate previews and mode-specific controls.

| Boundary | Responsibility |
|---|---|
| Receives | Current stream/candidate, capture status, confirmed snapshot and permitted policy. |
| Produces | Accessible camera/preview workspace and explicit confirmation intentions. |
| Consumers and dependencies | Controller, transcript surfaces and live browser acceptance. |
| Never store here | Appending candidate text locally, fake detection overlays or scientific threshold sliders. |

## Directory contents

| Entry | Purpose |
|---|---|
| [RecognitionWorkspace.tsx](RecognitionWorkspace.tsx) | Compose the reusable translator header, camera, recognition and transcript panels. |
| [pages/AlphabetTranslatorPage.tsx](pages/AlphabetTranslatorPage.tsx) | Open the Alphabet mode workspace against live backend readiness. |
| [pages/WordTranslatorPage.tsx](pages/WordTranslatorPage.tsx) | Open Word mode and honestly show model availability. |
| [components/](components) | Shared camera, candidate, header and transcript components. |
| [translator.css](translator.css) | Responsive workspace styles based on the Signova home design tokens. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
