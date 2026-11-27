# Signova frontend

React, TypeScript, and Vite browser client for the Signova v1 FastAPI service.
The Word and Alphabet translator routes share one camera/session controller,
one REST/WebSocket contract layer, and a common responsive workspace.

## Run locally

Use a maintained Node.js LTS version supported by Vite.

```powershell
cd C:\Users\user\Signova\frontend
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Open the local URL printed by Vite. The defaults in `.env.example` use the
backend at `http://localhost:8000`; override these public URLs in `.env.local`
if the backend uses another local origin. Vite does not read `.env.example`
automatically. Restart the dev server after changing environment values.

The backend's exact setup, trusted alphabet artifacts, and run command are in
[backend/README.md](../backend/README.md). The alphabet model is available only
when the backend successfully loads its checkpoint and hand detector. The Word
mode remains unavailable until `/models` reports it ready. The UI never fakes a
candidate or sends frames for an unavailable mode.

## Routes

- `/` — Signova landing page and mode entry.
- `/translator/alphabet` — live Alphabet Translator.
- `/translator/words` — Word Translator with live readiness from the backend.

The landing page preview is explicitly illustrative; it is not a model result.
Camera access begins only after the user presses **Start camera**. Recognition
requires a ready model, an authenticated socket, and an explicit **Start
recognition** action.

## Scripts

```powershell
npm run dev
npm run build
npm run preview
npm test
npm run test:e2e
```

Playwright browser tests need browser binaries installed with
`npx playwright install chromium`.

## Integration boundaries

- REST, WebSocket, snapshot ordering, and frame limits follow
  [REST API v1](../docs/contracts/rest-api.md) and
  [WebSocket protocol v1](../docs/contracts/websocket-protocol.md).
- The browser validates catalogues, session snapshots, candidates, and live
  events at runtime.
- The session capability is held in memory and never placed in a URL or log.
- Candidate events update only the preview. Transcript text comes from
  confirmed backend snapshots.
- Camera access is video-only, user-initiated, and released when capture stops
  or the translator unmounts. Frame sampling is unmirrored and single-flight,
  bounded by the backend model catalogue and matching frame acknowledgements.
- Camera samples are transiently encoded for recognition; there is no
  MediaRecorder or frame persistence.
- Local Copy and TXT download use the visible confirmed snapshot. Editing,
  Clear, End, Delete, and Alphabet Space use the corresponding authorized REST
  commands.

The controller reports a model as unavailable if the catalogue is unavailable
or has no ready entry. A local camera preview does not indicate recognition is
active.
