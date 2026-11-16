# Model packages and backend adapters

Owner: Ali for the common adapter boundary; Osama for alphabet semantics; Bavly for word semantics; Basil for data/recipe lineage. Sources: Ali §§8–10, Osama §§3–4/11/22–25, Bavly §§4/10/22–24. This specification describes future interfaces; no classes, predictor functions, schemas or fake adapters are implemented.

## Input boundary

Adham sends only the documented v1 JPEG messages to Ali. Ali validates and decodes into RGB in memory, orders samples, owns bounded scheduling and chooses the adapter from immutable session mode. Models receive their approved numerical/decoded representation, not arbitrary browser JSON. Owners must specify exact tensor names, dtype, axes, shape, batch conventions, color, orientation, handedness, crop/pad/resize/interpolation, range, normalization, missing-evidence encoding and any training-fitted parameters. Every dimension is **TBD per model**; neither the image example nor a feature vector from the board is a universal input.

For temporal input, specify timestamps and units, required rate, window/length bounds, stride, sign/context placement, gap tolerance, ordering, padding/length masks, interior presence masks, warmup and reset behavior. Ali and Bavly must choose whether the word adapter receives decoded RGB frames/times or precomputed features; do not expose two conflicting public interfaces. Whole-window support, live-window support and automatic completion are independent capability statements. A clip-only predictor cannot become live-compatible just because the UI adds manual Confirm.

## Common evidence and normalization

Ali's handbook proposes `preprocess(samples:list[bytes]) → array` and `predict(tensor) → Prediction`, with adapter `version`. Bavly proposes package-facing `load_model(package_dir)`, `reset_stream(stream_id)`, and `predict_window(frames_rgb,timestamps_ms,context)`. They describe different layers: the backend adapter wraps the owner package. Exact public callable signatures/reset context still require joint approval; no source interface is declared yet.

| Shared internal field | Meaning |
|---|---|
| `label_id:string\|null` | Trusted stable ID from that model's ordered map, never a free-form generated class |
| `text:string\|null` | Approved Arabic display text mapped from ID |
| `score:finite number 0..1` | Ali's proposed shared numeric score; not calibrated accuracy |
| `neutral:boolean` | True only with evaluated defined neutral/release evidence |
| `usable:boolean` | Recognition evidence is usable under the released model/quality policy |

Adapter `version` ties evidence to the selected immutable release. Model-owner outputs may additionally include `model_version` and safe `reason` diagnostics; Ali translates these and does not expose model internals as browser fields. Unusable/unknown/no-hand/transition are not neutral. Public candidates are emitted only from accepted usable evidence, and their scores remain non-null.

**Unresolved conflict:** Bavly's rejection examples use `score:null`; Ali's common Prediction requires a number, while Osama permits 0.0 when no meaningful score exists. Recommendation: keep Ali's shared type, translate absent raw score to a documented 0.0 sentinel only with `usable:false`, and preserve safe rejection reason separately. This needs joint acceptance; a sentinel is never confidence or permission to commit. See Q09 in the decision log. Data labels may use `text_ar`; public REST/WS keeps `text`. Stable semantic IDs and model-specific class indices must never be conflated.

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

Ali reproduces each reference predictor from a fresh compatible environment on target hardware. Basil verifies lineage/labels and fixture permission. Adham verifies the same approved input through sampler/transport and correct preview/snapshot behavior. Hisham accepts documented scope after golden, rejection, concurrency, hold/repeat, reset and late-result tests. Accuracy and software correctness are separate evidence. See [model release runbook](../runbooks/model-release.md).
