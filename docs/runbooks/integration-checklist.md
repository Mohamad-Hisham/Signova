# Integration acceptance checklist

Owner: Hisham; implementation evidence from the named module owners. This is a future acceptance plan, **not a record of passing application tests**. Mark items complete only with actual versions, hardware/browser, fixtures, results, responsible reviewer and date.

| Area | Acceptance evidence | Owners |
|---|---|---|
| Scope and vocabulary | Approved sign variety, exact supported alphabet/words, model map and reviewed English-delivery contract; unsupported signs not guessed | Hisham, Basil, Osama, Bavly, Ali, Adham |
| Data | Rights/source pin/hash, reviewed labels/boundaries, signer/parent/duplicate grouping, train-only transforms, frozen split/test exposure and fresh receiver first batches | Basil with model owners |
| Runtime startup | Both approved model runtimes compatible, checksums verified, load once, warmup/golden tests; live 200 separate from required-mode ready 503; no fake release | Ali, Osama, Bavly |
| Create/access | Revision/state 0 paused snapshot, token once/hash only, no token in URLs/logs, missing 401/wrong generic 404, cross-session isolation, capacity errors | Ali and Adham |
| Socket | Exact Origin, first auth timeout, one socket, correct envelope, every client/server type, no binary v1, heartbeat and graceful overload | Ali and Adham |
| Camera | Deliberate permission, audio off, truthful preview, cancel late permission, dimensions/aspect/unmirrored JPEG sizes, no overlapping sends; tracks stopped on every stop/failure/navigation | Adham |
| Frame/window | Matching acknowledgement only, old ack cannot unlock new stream, bounded queues, ordered sample/window, long-gap reset, insufficient_rate honesty, per-stream extractor isolation | Ali, Adham and model owners |
| Preview/Confirm | Candidate never appends; stable eligible fresh confirmation commits once; REST and socket same revision render once; simultaneous confirms cannot both consume | Ali and Adham |
| Repetition | Held word/letter once; deliberate release→same sign twice; manual Confirm-success→Pause→Start valid; different label cannot bypass latch | Ali, Bavly, Osama and Adham |
| Automatic words | Independent neutral/completion evidence; initial release arming; stale/unknown/gap cancels; one event per segment; disabled unless complete path passes | Bavly, Ali, Basil, Hisham |
| Alphabet | Exact letter IDs/text, logical concatenation, explicit paused Space, leading/repeated Space errors, no automatic words/grammar | Osama, Ali and Adham |
| Transcript edits | Pause first, separate dirty draft, full replacement/IDs, null provenance on change, NFC/LF/code-point limits, empty-list allowed, no partial writes, conflict preserves draft | Ali and Adham |
| Retries/order | Same key/body one success, key conflict, eviction/uncertain outcome reconciliation, independent revision/state/event ordering, stale Start cannot resume after Pause | Ali and Adham |
| Clear/Delete | During active encode/inference old frames/results/caches/queued responses cannot revive text; recovery disarmed; offline removal barrier resolved before display/capture; no false server-success | Ali and Adham |
| End/expiry | End read-only window/terminal behavior resolved, no revision change, Delete usable, request/sweeper cleanup, bounded content-free tombstones; restart loses RAM honestly | Ali and Adham |
| Recovery | Off by default; opt-in only, bounded validated sessionStorage with confirmed state only; opt-out/Clear/End/Delete remove it; reconnect paused; local copy after restart never silently uploaded | Adham and Ali |
| Copy/export | Explicit gestures, denied clipboard fallback, local offline download, server current-revision export/204/409/headers, mixed Arabic/numbers/punctuation and draft distinction | Adham and Ali |
| Accessibility/help | Keyboard/focus/dialog/IME/200% zoom/mobile, RTL/LTR isolation, no preview announcement storm, permitted validated sign examples and honest scope | Adham, Basil and model owners |
| Privacy and reliability | No default recordings/history/database/Redis/accounts/training collection; no content/secret logs or replay analytics, one worker/replica, measured bounded memory/load/native timeouts | Ali, Adham, Basil and Hisham |
| Scientific evidence | Per-class/group support, macro metrics, rejection/coverage/negatives; clip and live event results separated; named hardware p50/p95 and full-window delay, no target presented as result | Osama, Bavly and Basil |
| Final handoff | Reproducible tested locks, source/release references, matching contracts, model cards, browser matrix, known limitations, rollback and rehearsed Dec 1 scope | All; Hisham accepts |

Development simulations can later test session/UI software without real weights, visibly labeled. They do not demonstrate recognition accuracy or permit fake output in release. No app tests, mocks, model fixtures or passing metrics are implemented by this scaffolding task.
