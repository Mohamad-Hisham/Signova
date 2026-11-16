# Signova live WebSocket protocol v1

Owner: Ali; consumer/reviewer: Adham. Sources: Ali §§10/15–19/23–26; Adham §§11–13/16–20/25. No handler or transport is implemented. Endpoint: **`/api/v1/ws/sessions/{sid}`**. Use `wss` for deployment, `ws` only for localhost development. Capabilities never go in URLs or query parameters.

## Connection and authentication

Check exact handshake Origin independently of HTTP CORS. Browser-only deployment rejects missing Origin unless an explicit test-client policy permits it. After accepting a bounded connection, require the first `auth` JSON message within 5 seconds. Allocate no camera queue before successful authentication. Validate capability, session, status and expiry. Allow one authenticated socket per session; reject the second with 1008 `SOCKET_ALREADY_CONNECTED`, preserving the first socket. Ended-session auth is rejected; REST uses 409 `SESSION_ENDED` while a WebSocket rejection follows its policy close semantics.

Reply `session.ready` with a full snapshot and confirmation policy. Reconnection sets paused, invalidates old stream/candidate, increments state_version and requires explicit REST Start. `last_event_seq` is informational; there is no durable replay guarantee. Frames are never replayed to rebuild transcript state.

## Client objects

Each includes `protocol_version:1` and `type`. Unknown keys or message types are rejected. Only these three types exist; binary frames are unsupported. Start, Pause, Confirm, Space, replace, Clear and End use REST.

| `type` | Other fields | Meaning and expected response |
|---|---|---|
| `auth` | `session_token:string`; optional `last_event_seq:int≥0` | First message only; session.ready or close 1008 |
| `frame` | `stream_id:string`, `frame_seq:int≥1`, `capture_ms:finite number≥0`, `width:positive int≤640`, `height:positive int≤480`, `mirrored:false`, `image_b64:string` | Capturing/current stream only; strict base64 JPEG without data URL prefix; frame.ack and possible candidate/transcript notifications |
| `ping` | `nonce:string` length 1..64 | Every 15 seconds; pong with identical nonce; no revision or idle lifetime extension |

`frame_seq` strictly increases from 1 within a new stream. `capture_ms` is browser monotonic capture time; it helps order samples but cannot establish cross-machine latency. Server arrival time uses its own monotonic clock. Validate lengths/rate before parsing/decoding; check format, JPEG magic, dimensions and pixel count against real Pillow decoding, guard decompression bombs, require declared/decoded dimensions to agree. Reject NaN, infinity, stale/out-of-order frames and extra keys before model work.

Limits initially: 163,840 JPEG bytes; 262,144 total UTF-8 JSON bytes; dimensions at most 640×480; negotiated rate at most 10/second. Preserve aspect ratio and unmirrored bytes. Feature extraction, color conversion and preprocessing are server-side and model-specific. The v1 message has no browser landmark, upload-finished, stop-clip or transcript-edit field.

## Server envelope

Every server message requires `protocol_version:1`, `type:string`, `event_id:string`, `event_seq:int≥0` increasing session-wide, `session_id:string`, `at:UTC ISO timestamp`, `data:object`. `event_seq` includes acknowledgements and previews; it is not transcript revision. [REST](rest-api.md) defines Session, Transcript, Item, Candidate and Error fields.

| `type` | Exact `data` fields | Required frontend effect |
|---|---|---|
| `session.ready` | `session:Session`, `confirmation_policy:manual\|automatic_with_manual_fallback` | Accept full paused snapshot; wait for explicit Start |
| `session.state` | `session:Session`, `reason:start\|pause\|limit` | Merge text revision/capture version independently; stop sending if not capturing |
| `frame.ack` | `stream_id:string`, `frame_seq:int`, `outcome:processed\|discarded`, `reason:string\|null`, `processing_ms:finite number≥0` | Release only the matching outstanding stream/sequence slot; processed is not recognition or confirmation |
| `candidate.updated` | `candidate:Candidate\|null` | Preview only for active stream while capturing; null clears preview; never append transcript |
| `transcript.updated` | `session:Session`, `cause:commit\|replace\|clear\|space`, `command_id:string\|null`, `committed_item_id:string\|null` | Apply canonical transcript once by revision/item identity; automatic commit command_id is null |
| `pong` | `nonce:string` | Match heartbeat without extending idle expiry |
| `warning` | `code:string`, `message:string`, `frame_seq:int\|null` | Recoverable continuity/rate/quality guidance; no invented text |
| `error` | `error:{code,message,retryable,details}`, `request_id:string`, `related_frame_seq:int\|null`, `command_id:null` | Safe error envelope plus context; no state change unless separate state event follows |
| `session.ended` | `session:Session`, `reason:user` | Stop resources, remove recovery and show read-only review; close 1000 |
| `session.expired` | `reason:idle\|absolute\|reconnect_timeout` | No transcript payload; stop capability use; close 1000 |
| `session.deleted` | `reason:user` | No transcript payload; erase local session state; close 1000 |

Frame discard reasons: `stale_stream`, `stale_frame`, `gap_reset`, `rate_limit`, `paused`, `overload`. `insufficient_rate` is a warning about unsatisfied model sampling requirements, not an invented frame-discard enumeration. Warning code vocabulary beyond documented values and outbound queue bounds still need owner agreement.

## Flow control, cancellation and recovery

Browser: at most one in-flight sample; only a matching frame.ack releases it. Use a second `bufferedAmount` guard (initial threshold 256 KiB). Missing acknowledgement initially 3 seconds triggers stop/reconciliation, not extra sends. Do not overlap asynchronous sampling calls. Drop stale encodes when local generation changes.

Server: one bounded pending sample, one current owner-approved temporal window, initially ≤60 samples, one serialized writer. Acknowledge processed or discarded samples; window-warmup processing is not a candidate. A queue overflow, out-of-order frame or initially >500 ms gap resets incomplete temporal evidence and the candidate gate. Report the break honestly. If model-required sampling cannot be sustained, emit insufficient_rate and use only a model-supported approved fallback.

Control/snapshot events are reliable within a live connection; previews may be coalesced. If bounded writer delivery cannot keep up, close 1013 and recover by full snapshot. No persistent replay log exists. Never block every session waiting for an outbound writer or native inference under a session lock.

Pause/Clear/disconnect/End/deletion/expiry invalidate the generation, drop pending recognition and discard late model results. Pause is not word completion. Confirm must succeed before Pause in the manual fallback. On failure Adham stops tracks and sampling, discards candidate and reconnects approximately 1, 2, 4, 8 seconds then ≤15 seconds with jitter, only for a nonterminal live session. After 45 seconds without valid messages/pong treat the link as failed. Heartbeats run every 15 seconds. Reconnect grace initially 120 seconds; no auto-resume or frame replay.

## Close codes

| Code | Meaning and behavior |
|---|---|
| 1000 | Normal End/Delete/expiry; no reconnect after deliberate terminal action |
| 1007 | Malformed/unparseable message; emit safe error if possible then close |
| 1008 | Authentication/Origin/socket ownership/repeated policy violations; fix policy cause |
| 1009 | Oversized message; reject without decoding |
| 1011 | Backend failure; preserve local confirmed view and reconcile nonterminal session |
| 1013 | Temporary overload or writer pressure; bounded recovery then full snapshot |

A browser may observe an abnormal close without the intended final event. Reconcile an otherwise nonterminal session through authorized GET; do not claim terminal success from a lost connection. No tokens, frames, private text, rejected payload values or stack traces appear in events/logs.
