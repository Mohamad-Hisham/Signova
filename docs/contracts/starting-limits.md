# Initial engineering settings and evidence requirements

Owner: Ali with Adham/model-owner review; Hisham approves release limits. Sources: Ali §§1/10/13–19/23/25–28 and Adham §§11–19/24–25. These are starting engineering settings or proposed targets, not measured capacity, accuracy or guaranteed performance. Manifest-specific requirements remain TBD.

| Area | Initial value | Constraint/evidence |
|---|---|---|
| Python | 3.11 compatibility target | Verify both delivered runtimes together before selecting tested locks |
| Live backend topology | One process, one worker, one replica | RAM sessions cannot be shared or recovered across restart |
| Idle / absolute / reconnect grace | 900 / 3,600 / 120 seconds | Earliest applicable deadline; read/heartbeat do not extend idle |
| End review / tombstone | Up to 300 / 120 seconds | End capped by absolute expiry; deadline precedence/expiry DELETE semantics open |
| Expiry sweeper | At least every 15 seconds | Also check every authenticated request |
| Session / socket capacity | 20 sessions; one socket per session | Starting cap only; measure/load-test and lower if needed |
| Transcript limits | 2,000 items; 20,000 Unicode code points | Individual edit item 1..2,000 after NFC; validate complete mutation |
| Mutation success cache | 60 IDs per session | Oldest eviction, session-bounded; Clear purges content-bearing old replies |
| REST body cap | 128 KiB (131,072 bytes) | Enforce before parse; applies together with text/item limits |
| Creation / REST mutation rate | 5/minute/source IP; 30/minute/session | Initial settings; approved exact edge handling still future |
| JPEG dimensions / bytes | At most 640×480; 160 KiB (163,840 bytes) | Actual decoded dimensions agree with metadata, resource-bounded JPEG decode |
| WS message / sample rate | 256 KiB (262,144 bytes); initially at most 10 samples/s | Required model rate/window must fit and be evaluated |
| Browser / server pending admission | One in flight / one pending | Acknowledge processed/discarded; no stale backlog |
| Model sample window cap | Initially 60 samples maximum | Actual model need TBD; Bavly's teaching loader up to 120 is not an approved live window |
| Continuity gap | Initially >500 ms resets window | Final tolerance is representation-specific and evaluated |
| WS auth / heartbeat / link timeout | 5 s / 15 s / 45 s | No preauth camera queue; heartbeat does not renew idle |
| Client ack watchdog / bufferedAmount | Initially 3 s / 256 KiB | Stop/reconcile on failure, do not admit another pending frame |
| Reconnect backoff | Near 1, 2, 4, 8 s then ≤15 s plus jitter | Nonterminal session only, grace-bounded, explicit Start after recovery |
| Candidate support expiry | Initially 2 s | Refresh only on valid supporting observations; stale candidates cannot commit |
| Entry / exit score | 0.85 / 0.65 | Validation settings only; score is not measured accuracy |
| Stability / neutral dwell | ≥300 ms and ≥3 valid observations / ≥300 ms | Neutral must be independently defensible; correlated windows are not independent proof |
| Inference timeout | Initially 2 s measurement target | Native computation can continue; retain occupied capacity slot |
| Server p95 / completion target | <300 ms processing; useful word ≤1.5 s after boundary | Targets from Ali, measured stages/window delay and hardware required; conflicts with older board logged |
| Operational log retention | Suggested 7 days | Hisham approval pending; codes/counts/timings only, never payloads/secrets |
| Writer queue / tombstone total capacity / rate bursts | TBD | Must be bounded; agree exact values before implementation acceptance |

No model dimension, feature count, vocabulary size, final frame window, accuracy or live-completion capability is established here. Do not put the 20-frame or 128-feature teaching examples into a fake release manifest. For insufficient rate, reject/pause and disclose the model mismatch; only use a model-supported manual segmented flow.
