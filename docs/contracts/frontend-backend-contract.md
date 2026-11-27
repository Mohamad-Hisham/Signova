# Frontend/backend behavior agreement

Owners: Ali and Adham; Hisham accepts product behavior. Read [REST](rest-api.md), [WebSocket](websocket-protocol.md), [starting limits](starting-limits.md) and [runtime flow](../architecture/runtime-data-flow.md) together. These documents centralize handbook-local API/WS/screens references without changing their public fields.

## Separate authority and state

Backend RAM owns the active session and confirmed transcript. Browser serializable state keeps accepted transcript revision, capture state_version, current candidate, connection status, editor draft/base revision/dirty flag, pending command outcomes, deletion barrier and recovery eligibility separately. A controller owns token, media tracks, socket/listeners, timers, local generation and outstanding frame pair outside render state. One controller opens one camera and one socket.

Candidates never append frontend transcript text. Server revision orders transcript; state_version orders capture/status; event_seq orders socket events. Merge domains independently, verify session identity and local connection generation, and honor removal barriers before displaying any response. Equal/older text cannot roll back a newer transcript. The same commit arriving by REST and socket appears once and is announced once. A dirty editor survives incoming snapshots.

| Surface/action | Frontend responsibility | Backend authority/output |
|---|---|---|
| Homepage and mode selection | Display available modes, model readiness, privacy and unchecked recovery option. Open the camera after a deliberate user action. | Public catalogue, vocabulary and readiness. Create a paused session for a ready mode. |
| Start | Deliberate camera permission, usable video, authenticated socket, current versions; no send before success | New stream and capturing snapshot; revision unchanged |
| Live Translator and Preview | Bounded JPEG/ack flow; candidate/eligibility display; no fake skeleton or direct model imports | Validate/preprocess/route; current candidate only |
| Confirm word/letter | Current eligible candidate, stream/revision and one command UUID; disable pending | Consume one current segment; snapshot plus item_id; duplicate attempt conflicts |
| Pause | Immediately stop sampler/tracks and local generation; reconcile command outcome | Discard all pending evidence, invalidate stream; never classify final window |
| Switch alphabet or word | Read model readiness, use the active session's token and expected versions, discard the old preview after success, and reset frame sequence for the new stream | Change the active adapter in the same session while preserving the confirmed transcript and revision |
| Space | Alphabet only, paused, fresh revision/UUID | Explicit user space; reject leading/repeated spaces or wrong mode |
| Transcript editor | Pause and reconcile first; separate draft; Save/Cancel and IME-safe RTL; protect uncertain saves | Full validated ordered replacement; changed text becomes user-authored; revision +1 |
| Copy | Explicit clipboard gesture; confirmed text versus draft clearly labeled; honest denied-permission fallback | No API mutation or revision change |
| Download | Explicit local UTF-8 Blob or authorized exact-revision fetch; revoke object URL; offline local option | No-store TXT export; 204 empty, 409 stale; no server file/history |
| Clear | Confirm meaningful removal, stop tracks, erase draft/preview/recovery and hide stale content until resolved | Empty paused snapshot, higher revision/state version, purge old text caches/late evidence |
| End review | Stop resources; remove recovery; keep read-only view and memory token only during review | Ended snapshot, socket close; brief read/export/delete window |
| Delete | Deliberate removal; barrier and minimal pending credential; discard after acknowledgement | Immediate RAM erase, content-free event/tombstone; 204 |
| Sign Library and About/Help | Show approved supported scope, limitations, permitted examples and accessible guidance | Public model-compatible Arabic vocabulary; English mechanism still undecided |

Mode change preserves the session ID, token, and transcript. A capturing session receives a new stream ID on the same socket. Keep the current view and stream if the target mode returns `MODEL_UNAVAILABLE`. A confirmed hold stays latched until evaluated release or an explicit Pause/Start. The current alphabet checkpoint uses the manual Pause/Start flow after confirmation. Automatic completion requires evaluated release evidence.

## Camera and permission lifecycle

Adham requests video only (`audio:false`) after a gesture, preserves aspect ratio, mirrors only the preview, and waits for usable metadata/playback before sampling. On permission denial, missing/busy camera or insecure context, show specific guidance and no repeated prompt loop. Late permission after Cancel stops the newly returned tracks. A simpler-constraint retry, if used, is once and remains video-only.

Pause, Clear, End, Delete, expiry, socket failure, confirmed navigation, hidden-page handling and teardown cancel scheduling/encodes, stop every track, clear video ownership and discard candidate. `video.pause()` alone does not release the device. Camera switching stops the old stream and requires a new capture generation. Hidden/background pages pause best effort; returning requires reconciliation and explicit Start. React Strict Mode cleanup must remain correct.

## Pending actions and conflicts

A deliberate mutation stores exact UUID/method/path/body with its expected versions. A timeout/abort does not prove rollback. Retry the original identity or fetch a snapshot; never increment expected revision and blindly repeat a Confirm with a new key. Preserve drafts on conflict; show current server text and let the user review/reapply. Capture actions also compare expected_state_version to reject a delayed old Start after Pause.

Copy/download never claim permanent storage, successful file save without browser evidence, or session ending. Server export of an unsaved draft is disabled/clearly separated from optional local draft export. Local deletion does not erase clipboard or downloaded files.

## Recovery and removal

Default display/draft/secret storage is tab memory. Recovery is off by default and separate from camera permission. Explicit opt-in at creation permits a versioned sessionStorage record with session ID/mode/token, last confirmed snapshot, creation time and bounded expiry; no camera samples, candidates, drafts, pending command bodies or private logs. Validate shape/expiry on every load and handle storage failure. The cap is the earlier server absolute deadline or 60 minutes from creation. Turning off removes it immediately; turning on later needs an ended old session and new opted-in session. Clear removes/disarms it so a generic persistence effect cannot restore it.

After connection loss: stop tracks, clear candidate, keep confirmed visible text, retry with bounded backoff within grace, accept a full paused snapshot and require explicit Start. No offline recognition or camera replay exists. Refresh without opt-in loses credentials/text. With opt-in, try authorized GET/socket; if server is gone/restarted, label cached text as a recovered local copy and allow only local actions or deliberate fresh start, never silent re-upload.

Offline Clear/Delete removes browser content immediately and hides all stale responses. Retain only minimal in-memory credentials/removal intent until the server action completes. For pending Clear, retrieve current revision without rendering private content and clear before lifting the barrier. For Delete, delete before reopening capture. Until acknowledged say server removal is pending; if tab closes, TTL is the fallback. End/acknowledged Delete/known expiry/protocol incompatibility stop reconnect loops.

## Accessibility and acceptance

Arabic uses logical Unicode with lang ar/RTL; English/IDs/URLs receive correct LTR isolation. Preserve IME composition and meaningful Arabic distinctions. Use semantic labeled buttons/textarea/dialogs, managed dialog focus, visible focus, keyboard actions and 200% zoom; polite announcements for commits/status, not every preview/ack. Show status in words as well as color. No raw HTML rendering, third-party session replay or automatic recording/caching.

Future Vitest/Testing Library/Playwright checks cover duplicate/stale snapshots, independent version domains, dirty draft, pending UUID reuse, camera cancellation/cleanup, old acknowledgements, denied clipboard/storage, Arabic export, holds/repeats, Clear during encode/inference, offline removal, refresh consent and backend restart. No application tests exist or run in this scaffold.
