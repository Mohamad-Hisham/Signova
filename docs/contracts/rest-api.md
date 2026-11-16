# Signova REST API v1

Owner: Ali; consumer/reviewer: Adham; Hisham coordinates changes. Source: Ali §§7/11–14/25–26 and Appendices A–B; Adham §§14–15/19/21–25 and Appendix A. This is a transcription of the agreed handbook contract, not a generated API or running implementation. No alternative routes or English translation fields are introduced. See [open questions](../architecture/decisions/open-questions.md) for missing decisions.

All paths below include **`/api/v1`**. JSON is UTF-8. Public modes: `word` and `alphabet`. Unknown request fields are rejected. Session IDs, stream IDs and item IDs below are server-issued; shortened example IDs are illustrative. Real session/stream IDs use UUIDs and a separately generated random secret.

## Access and response conventions

Health, models, vocabulary and session creation are public. Every existing-session read, mutation, export, end and delete requires `Authorization: Bearer <session_token>`. The capability grants access to one temporary session; it is not a login or user account. Creation returns it once; server stores only its SHA-256 hash and compares safely. It never appears in URLs, logs, examples containing real secrets, or public environment variables. No public session listing exists.

JSON bodies use `Content-Type: application/json`. Every JSON mutation of an existing session requires `Idempotency-Key` with a UUID. DELETE has no body or revision requirement and is already idempotent. POST creation is not automatically retried. Session and export responses use `Cache-Control: no-store`. CORS allows exact origins, `Authorization`, `Content-Type`, `Idempotency-Key`, and exposes `X-Transcript-Revision` for export. CORS does not authenticate requests or replace WebSocket Origin checks.

Unless listed otherwise, snapshot responses are `{session: Session}`; Confirm also returns `item_id`. No-body routes must receive no JSON body, including no empty object. Request validation failure is 422; a valid request conflicting with current state is 409. Ordinary REST JSON is initially limited to 128 KiB. Limits apply together with item/character limits; a nominally valid item list can still exceed the encoded body cap.

## Exact shared response objects

| Object | Required fields and constraints |
|---|---|
| `Session` | `session_id:string`, `mode:word\|alphabet`, `status:paused\|capturing\|disconnected\|ended`, `state_version:int≥0`, `expires_at:UTC ISO string`, `absolute_expires_at:UTC ISO string`, `idle_timeout_seconds:positive number` (initial 900), `reconnect_grace_seconds:positive number` (initial 120), `model_version:string`, `stream_id:string\|null`, `recovery_enabled:boolean`, `transcript:Transcript` |
| `Transcript` | `revision:int≥0`, `items:Item[]`, `text:string`, `updated_at:UTC ISO string`. Text is derived from items, never a second editable authority. |
| `Item` | `item_id:string`, `text:string`, `kind:word\|letter\|space\|manual`, `source:model\|user`, `label_id:string\|null`, `score:finite number 0..1\|null`, `model_version:string\|null`, `confirmed_by:auto\|manual\|edit`, `created_at:UTC ISO string` |
| `Candidate` | `candidate_id:string`, `stream_id:string`, `mode:word\|alphabet`, `label_id:string`, `text:string`, `score:finite number 0..1`, `stable:boolean`, `eligible:boolean`, `expires_in_ms:int≥0`, `model_version:string` |
| Error response | `error:{code:string,message:string,retryable:boolean,details:object}`, `request_id:string`; no transcript text, rejected private values, image bytes, token or traceback |

`expected_revision` and `expected_state_version` are integers ≥0, never booleans or numeric strings. Timestamps are UTC ISO strings for display; timers use server monotonic time. `expires_at` is the earliest applicable current deadline. Mode and model version are fixed for a session. Field/string/date maxima not provided by the handbooks remain owner validation decisions; do not silently publish extra schema fields.

Word rendering joins nonempty item texts with one normal space. A phrase label remains one item. Alphabet rendering concatenates letter/manual text with literal spaces only for space items. Text uses NFC, line endings LF, logical Unicode order; reject control characters other than LF and TAB and preserve meaningful Arabic distinctions. User item text is 1–2,000 Unicode code points after normalization; full transcript maximum initially 2,000 items and 20,000 code points. Count code points in JavaScript, not UTF-16 units.

## Public catalogues

| Method and exact route | Request | Success and response fields | Failure behavior |
|---|---|---|---|
| GET `/api/v1/health/live` | No body; public | 200 `{status:"alive"}`; no model computation | Generic 500 for unexpected service failure |
| GET `/api/v1/health/ready` | No body; public | 200 or 503 with the **same** shape `{ready:boolean,modes:{alphabet:boolean,word:boolean},required_modes:(word\|alphabet)[]}` | 503 readiness is intentionally not an ordinary error envelope; no paths/traces |
| GET `/api/v1/models` | No body; public | 200 `{models:ModelEntry[]}` including unavailable modes with `ready:false` | No fake-dev model in a release catalogue; unexpected failures use safe errors |
| GET `/api/v1/vocabulary?mode=word` | Required `mode=word\|alphabet`; no body; public | 200 `{mode,model_version,labels:[{label_id:string,text:string,kind:word\|letter}]}`; complete public supported list, unique IDs and stable sorted order | 422 missing/invalid mode; 503 `MODEL_UNAVAILABLE` without approved mapping; exclude internal neutral/unknown classes |

Every `ModelEntry` requires `mode`, `model_version`, `ready:boolean`, `confirmation_policy:manual|automatic_with_manual_fallback`, `input:InputLimits|null`, `transcript_limits:{max_items:positive int,max_characters:positive int}`. `InputLimits` requires `format:"jpeg"`, `max_width`, `max_height`, `max_jpeg_bytes`, `max_message_bytes`, `max_fps` (positive bounded integers), `required_sample_fps:positive number|null`, `window_samples:positive int`, `mirrored:false`. Transport starting values are 640, 480, 163840, 262144 and 10 respectively. Required rate/window come from each validated manifest, never from the illustrative 20-frame example. For a non-temporal model use `window_samples:1` and `required_sample_fps:null`. For an unavailable artifact without a validated manifest use `input:null`. Incompatible runtime input settings fail readiness rather than being fabricated.

The v1 vocabulary objects contain Arabic `text` only. Approved English data and its frontend distribution mechanism are still a recorded decision; adding `text_en` or another endpoint silently would change this contract.

## Session and transcript endpoints

All rows except creation require the bearer capability. JSON mutation rows also require the command UUID header. These failure cases are additional to common validation, credentials, expiry, rate, payload and safe server errors.

| Method and exact route | Request fields | Success and revision/state behavior | Specific failures |
|---|---|---|---|
| POST `/api/v1/sessions` | `{mode:word\|alphabet,recovery_enabled:boolean}`; recovery defaults false | 201 `{session_token:string,session:Session}` once; paused, `stream_id:null`, revision 0, state_version 0; initial empty items/text | 422 malformed mode/body; 503 requested mode unavailable; 429 `SESSION_LIMIT`/creation rate; lost response is uncertain, no automatic retry loop |
| GET `/api/v1/sessions/{sid}` | No body | 200 full snapshot; no token; read does not refresh idle deadline | Generic 404 wrong secret/unknown ID; matching tombstone 410 |
| POST `/api/v1/sessions/{sid}/capture` | `{expected_revision,expected_state_version,action:"start"\|"pause"}` | 200 snapshot. Start requires authenticated socket, creates fresh stream and increments state_version. Pause invalidates stream, stops capture, drops pending evidence, increments state_version; transcript revision unchanged. Never classify a final buffer on Pause. | 409 `REVISION_CONFLICT`, `STATE_CONFLICT`, `SOCKET_REQUIRED`, `ALREADY_CAPTURING`, `SESSION_ENDED`; repeated Pause semantics beyond cached retry remain a decision |
| POST `/api/v1/sessions/{sid}/confirm` | `{expected_revision,candidate_id:string,stream_id:string}` | 200 `{session,item_id:string}`; capturing/current eligible fresh unconsumed candidate commits once, revision +1; held-sign latch remains | 409 `CANDIDATE_UNAVAILABLE`, `STALE_STREAM`, `REVISION_CONFLICT`, `SESSION_ENDED`; manual confirmation never bypasses latch |
| POST `/api/v1/sessions/{sid}/space` | `{expected_revision}` | 200 snapshot; paused alphabet only; adds one `text:" "`, `kind:"space"`, `source:"user"`, `confirmed_by:"manual"`, null score/label/model; revision +1 | 409 `WRONG_MODE`, `CAPTURE_ACTIVE`, `SPACE_NOT_ALLOWED` at start or after a space, revision conflict |
| PATCH `/api/v1/sessions/{sid}/transcript` | `{expected_revision,items:[{item_id?:string,text:string}]}` | 200 snapshot; full ordered replacement while paused; omitted items removed; new IDs server-generated; revision +1 even identical visible text; empty list valid | 422 empty item, duplicate/foreign/unknown ID, extra provenance fields, invalid text or limits; 409 `CAPTURE_ACTIVE`, revision conflict, transcript limit where applicable; validate all before mutation |
| POST `/api/v1/sessions/{sid}/transcript/clear` | `{expected_revision}` | 200 empty paused snapshot; capturing or paused allowed; invalidate stream, drop frames/candidate and content-bearing command/outbound caches, clear items, revision +1 and newer state_version; cache only this clear result; emit `transcript.updated` and `session.state` | 409 revision conflict/ended session; no partial clear or revival by old commands/results |
| GET `/api/v1/sessions/{sid}/export?format=txt&revision=R` | `format=txt`, current integer `revision`; no body | 200 exact derived current text, or 204 empty. `Content-Type:text/plain; charset=utf-8`, `Content-Disposition:attachment; filename="signova-transcript.txt"`, `Cache-Control:no-store`, `X-Transcript-Revision:R`; optional tested UTF-8 BOM. No revision change, disk write, end or clear. | 409 revision is not current; 422 unsupported format/invalid query; expired/deleted/unknown as common access rules |
| POST `/api/v1/sessions/{sid}/end` | `{expected_revision}` | 200 ended snapshot, revision unchanged, newer state_version; invalidate stream/buffers, emit `session.ended`, close 1000; read/export/delete review up to 5 minutes capped by absolute expiry | 409 revision conflict; mutations/socket auth on ended sessions fail `SESSION_ENDED`; repeated End/new-key behavior requires owner decision |
| DELETE `/api/v1/sessions/{sid}` | No body or expected revision; bearer only | 204; immediately erase frames/tensors/transcript/candidates/caches; content-free `session.deleted` then close 1000 when possible; authorized repeat 204 during 2-minute tombstone | 401 missing credential; generic 404 wrong/unknown/expired tombstone; expired-session DELETE behavior during expiry tombstone is not fully specified |

Changed or newly authored edit items use `source:user`, `kind:manual`, `confirmed_by:edit`, `score:null`, `label_id:null`, `model_version:null`. Unchanged existing items retain provenance. A simple whole-text editor may send one manual item only while it fits the per-item 2,000-code-point limit; the full-transcript limit does not waive this. Unsaved drafts are separate from confirmed snapshots and server exports.

## Ordering, retries and lifetimes

Under one per-session lock: authenticate/check expiry → inspect cached command → compare canonical method/path/body → compare revision (and state version for capture) → validate state/limits → atomically mutate → cache copied success → publish full snapshot. Do not await inference or socket delivery while holding the lock. Failures are not cached. Same key plus same request returns the original success; same key with changed method/path/body gives 409 `IDEMPOTENCY_CONFLICT`. Retry uncertain work with its exact original key/body. A corrected/new action gets a new key. Keep initially 60 successful mutation IDs, evict oldest; cache lives no longer than the session. After eviction do not guess success or blindly change revisions to repeat a confirm.

Revision increments once per append, replacement, space or clear. Preview, capture start/pause, heartbeat, copy, export and end do not change it. State changes use state_version. Idempotency is bounded to the live cache; it is not durable exactly-once execution across restart. Two simultaneous keys cannot both consume one candidate.

Initial lifetimes: idle 900 seconds, absolute 3,600 seconds, disconnected grace 120 seconds; expire at the earliest applicable deadline. Valid user actions/admitted frames refresh idle; read and heartbeat do not. Request checks plus a sweeper at least every 15 seconds enforce cleanup. End's review deadline precedence relative to older idle/disconnect deadlines is explicitly unresolved. Deletion/expiry keeps only a bounded token-hash tombstone for 120 seconds, never text. Authorized access returns 410 `SESSION_DELETED` or `SESSION_EXPIRED`; afterward 404. One authenticated socket per session; reconnect returns paused with a fresh state version and no active stream/candidate.

## Safe errors

| Status/channel | `error.code` | Consumer behavior |
|---|---|---|
| 401 | `CREDENTIAL_REQUIRED` | Required secret missing; no unchanged retry |
| 404 | `SESSION_NOT_FOUND` | Wrong secret or unknown ID share generic response |
| 410 | `SESSION_EXPIRED`, `SESSION_DELETED` | Matching tombstone only; stop active session handling |
| 409 | `REVISION_CONFLICT` | `details.current_revision`; preserve draft and fetch authorized snapshot |
| 409 | `STATE_CONFLICT` | Reconcile capture state before a fresh action |
| 409 | `CANDIDATE_UNAVAILABLE`, `STALE_STREAM` | Wait for fresh evidence/stream; do not invent a commit |
| 409 | `CAPTURE_ACTIVE`, `SOCKET_REQUIRED`, `ALREADY_CAPTURING`, `SESSION_ENDED` | Explain required state transition |
| 409 | `IDEMPOTENCY_CONFLICT`, `WRONG_MODE`, `SPACE_NOT_ALLOWED` | Correct request without changing state |
| 413 / WS 1009 | `PAYLOAD_TOO_LARGE` | Reject before expensive decoding/partial application |
| 422 | `VALIDATION_ERROR` | `details.fields:[{path,reason}]`; never echo private rejected values |
| 429 | `RATE_LIMITED`, `SESSION_LIMIT` | Honor REST `Retry-After` seconds; bound retries |
| 503 | `MODEL_UNAVAILABLE`, `INFERENCE_TIMEOUT` | Pause recognition, preserve confirmed text |
| WS warning / 409 | `TRANSCRIPT_LIMIT` | Stop capture and preserve text; offer export/clear |
| 500 / WS 1011 | `INTERNAL_ERROR` | Safe generic message and request_id |

Illustrative conflict response (not a real session or executable fixture):

```json
{"error":{"code":"REVISION_CONFLICT","message":"Refresh before saving.","retryable":false,"details":{"current_revision":4}},"request_id":"example-request"}
```

Initial capacity/rate values are engineering settings in [starting limits](starting-limits.md), not server performance claims. See [WebSocket v1](websocket-protocol.md) and [frontend/backend behavior](frontend-backend-contract.md) for live events, failure recovery and deletion barriers.
