# Model packages and backend adapters

Ali owns the common adapter boundary, Osama owns alphabet semantics, Bavly owns word semantics, and Basil owns data and recipe lineage. The backend currently loads the local AASL31 alphabet adapter. The word mode requires its model release.

## Input boundary

The backend validates v1 JPEG messages in memory, orders samples, and schedules bounded inference on the adapter selected for the current stream. A mode change replaces the stream before the next frame reaches the target adapter. Model owners specify shape, color, orientation, handedness, crop, resize, normalization and any training-fitted parameters. Each adapter implements its model's own numerical representation.

For temporal input, specify timestamps and units, required rate, window/length bounds, stride, sign/context placement, gap tolerance, ordering, padding/length masks, interior presence masks, warmup and reset behavior. Ali and Bavly must choose whether the word adapter receives decoded RGB frames/times or precomputed features; do not expose two conflicting public interfaces. Whole-window support, live-window support and automatic completion are independent capability statements. A clip-only predictor cannot become live-compatible just because the UI adds manual Confirm.

## Common evidence and normalization

The backend adapter accepts a bounded window through `predict(frames: list[bytes], times_ms: list[float])` and returns a `Prediction`. It exposes its public model version, label map, window size, and confirmation policy. `reset_stream(stream_id)` resets model-specific stream state before a fresh inference window. The alphabet adapter evaluates one JPEG per call and shares read-only model weights.

| Shared internal field | Meaning |
|---|---|
| `label_id:string\|null` | Trusted stable ID from that model's ordered map, never a free-form generated class |
| `text:string\|null` | Approved Arabic display text mapped from ID |
| `score:finite number 0..1` | Ali's proposed shared numeric score; not calibrated accuracy |
| `neutral:boolean` | True only with evaluated defined neutral/release evidence |
| `usable:boolean` | Recognition evidence is usable under the released model/quality policy |

Adapter `version` ties evidence to the selected immutable release. Model-owner outputs may additionally include `model_version` and safe `reason` diagnostics; Ali translates these and does not expose model internals as browser fields. Unusable/unknown/no-hand/transition are not neutral. Public candidates are emitted only from accepted usable evidence, and their scores remain non-null.

**Unresolved conflict:** Bavly's rejection examples use `score:null`; Ali's common Prediction requires a number, while Osama permits 0.0 when no meaningful score exists. Recommendation: keep Ali's shared type, translate absent raw score to a documented 0.0 sentinel only with `usable:false`, and preserve safe rejection reason separately. This needs joint acceptance; a sentinel is never confidence or permission to commit. Ali and both model owners must agree this translation. Data labels may use `text_ar`; public REST/WS keeps `text`. Stable semantic IDs and model-specific class indices must never be conflated.

## Dependency and runtime responsibilities

Route/socket → session/recognition/command services → `backend/app/models/base.py` boundary → dedicated `alphabet.py` or `word.py` adapter → its owner's `ml/.../src/predict.py`, `preprocessing.py`, `model.py`, `decision.py`. Prediction must not import `train.py`, fit scalers, update weights, download artifacts, save frames or mutate transcripts. Networking code never needs raw logits, class-index arithmetic or framework-specific shapes.

Startup validates configured trusted package locations/checksums/runtimes, loads each selected model once, applies evaluation/inference modes where required, warms up and runs golden fixtures. Per-mode readiness becomes true only after success. Global readiness returns 503 if any release-required mode is unavailable; catalogue can still advertise the unavailable mode honestly. Never silently substitute `fake.py` or hot-swap maps/weights during active sessions.

Inference and expensive preprocessing run outside socket event loops/session locks with bounded runtime capacity. Use an owner-approved concurrency setting for non-thread-safe runtimes. Read-only weights may be shared; trackers, recurrent state, temporal buffers and gates must belong to one stream and reset on gaps/stops/disconnects. Timeout does not terminate native computation; retain its slot and discard stale output when it returns. Restart may be needed and loses sessions.

## Complete release handoff

Each owner provides an immutable versioned package, stored outside ordinary Git for binaries/restricted assets:

| Required deliverable | What Ali must be able to verify |
|---|---|
| Model manifest and trusted artifact/export | Stable model ID/version, file hashes, format, task/variety, provenance and approved use |
| Ordered labels and stable IDs | Output index, unique semantic ID, approved Arabic text; internal unknown/neutral classes separated |
| Preprocessing specification and implementation | Exact deterministic recipe, fitted values, extractor artifact/version if used, golden intermediate tolerances |
| Decision/rejection configuration | Score computation/logits/probabilities, calibration, thresholds, quality/reject policy and neutral capability |
| Temporal/capability specification | Approved sampling/window/reset behavior; classify-isolated/live-window/auto-completion support explicitly evaluated |
| Runtime requirements and prediction interface | Tested Python/package/OS/device requirements, callable entrypoint, concurrency and reset instructions |
| Golden fixtures | At least five small permitted fixtures per Ali's checklist, expected labels/usable/reject/neutral outcomes, score/tensor tolerances and provenance |
| Evaluation reports and model card | Per-class support, signer/group protocol, negative/coverage results, test exposure and hardware/latency/memory evidence |
| Integration instructions | First inference, startup/warmup, safe errors, compatibility matrix, rollback and known limitations |
| SHA-256 checksums | Exact delivered file bytes and metadata; numerical tolerances rather than assumed bitwise equality across runtimes |

Manifest semantics include input/output names/shapes/dtypes, class-map hash, recipe/decision version, dataset/split/label versions, framework/Python/provider versions, CPU/GPU needs and supported capability flags. Filename examples differ across owners (`classes.json` versus `labels.json`, `decision_policy.json` versus `decision.json`, `checksums.sha256` versus `SHA256SUMS`); manifests must declare actual paths rather than silently forcing identical package layouts. Metadata specifications stay in Markdown until real releases exist.

Ali reproduces each reference predictor from a fresh compatible environment on target hardware. Basil verifies lineage/labels and fixture permission. Adham verifies the same approved input through sampler/transport and correct preview/snapshot behavior. Hisham accepts documented scope after golden, rejection, concurrency, hold/repeat, reset and late-result tests. Accuracy and software correctness are separate evidence. See [team handoffs](../team/handoffs.md) for receiving-owner acceptance.
