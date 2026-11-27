# frontend/src/camera

Owner: **Adham**.

Permission/track ownership and bounded unmirrored JPEG sampling.

| Boundary | Responsibility |
|---|---|
| Receives | Explicit gestures, usable video, active stream, negotiated limits and matching acknowledgements. |
| Produces | Transient samples and honest camera status/cleanup. |
| Consumers and dependencies | app/sessionController.ts, api/liveSocket.ts and camera acceptance tests. |
| Never store here | MediaRecorder, background/offline frame queues, browser landmarks or saved user images. |

## Directory contents

| Entry | Purpose |
|---|---|
| [frameSampler.ts](frameSampler.ts) | Encode bounded unmirrored JPEG samples with matching-ack single-in-flight flow control. |
| [useCamera.ts](useCamera.ts) | Own one explicit video-only permission request and release its media tracks. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
