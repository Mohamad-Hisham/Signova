# Data, media and artifact governance

Owner: Basil for offline data; model owners for model packages; Ali/Adham for temporary application state; Hisham for acceptance and unresolved permissions. This is the project's engineering policy, not a determination that any external source is legally approved.

Keep four domains distinct: restricted originals/identity/consent evidence; approved offline developer/evaluation releases; reviewed public runtime labels/help/fixtures; and temporary live-session RAM. A source being downloadable or a manifest being pseudonymous does not make it safe for public Git or redistribution. The existing project license does not grant external dataset/model rights.

| Location | Allowed | Prohibited |
|---|---|---|
| Git documentation and metadata | Reviewed safe schemas, semantic IDs/labels, source/release references, hashes, aggregate reports and permitted evidence | Private identities/consent records, unreviewed sample manifests, source media, user text/tokens or restricted notebook outputs |
| `data/raw/`, `interim/`, `processed/`, `features/` | Ignored authorized local engineering payloads, subject to source policy; README/.gitkeep stay tracked | Application live database, automatic session collection or publishing payloads |
| External controlled dataset storage | Authorized originals/derivatives/releases with named access and source-specific retention | Unreviewed collection, indefinite copies contrary to source/withdrawal decisions |
| External model artifact storage | Trusted immutable approved releases, weights/exports, runtime evidence and permitted fixtures | Browser uploads selecting arbitrary model paths/URLs or silent replacement of a released version |
| Backend/browser live RAM | Current bounded frames/tensors, session/candidate state, authoritative temporary transcript, local draft/display | Default recordings, disk frame/transcript dumps, automatic training, database/Redis/history |
| Optional tab sessionStorage | Explicit opted-in unexpired last confirmed snapshot and minimal recovery credential/metadata | Default persistence, frames, candidates, drafts, command bodies, localStorage/IndexedDB history |

`.gitignore` excludes payload layers, media/archive binaries, checkpoints/tensors, environment/dependency/cache outputs, recordings/session dumps and secret formats. Approved metadata such as `.md`, safe `.csv`/`.jsonl`/`.json`, checksum files and release pointers can be tracked only after content review. Binary media is ignored everywhere by default; future tiny consented fixtures/public help assets need a narrow path-specific reviewed exception and rights/attribution record. An ignored directory does not provide access control, and ignore rules do not remove already tracked files.

Basil preserves permitted raw originals and lineage, logs derivative transformations, quarantines uncertain labels/rights and protects signer/session/parent/duplicate groups across evaluation boundaries. Fit transforms/augmentation only from train rules; record final-test exposure. Model owners maintain class order, recipes, evidence and versioned weights; Ali/Adham consume only the approved public subset. Scientific and product logs contain codes/counts/timings without user text, bytes, landmarks, secrets or session-linked label payloads.

No default user camera recording, correction-to-training feed or permanent transcript history exists. Camera permission, Copy, Download and recovery consent do not authorize data collection. A future collection program needs its own approved notice, scope, access, annotation, retention and withdrawal design before implementation.

Withdrawal traces affected originals, derivatives, caches, distributed releases and dependent trained models. Restrict/stop use, notify Hisham and authorized recipients, and record approved removal/replacement evidence. Removing a clip does not prove unlearning from weights; model owners/Hisham decide retraining/retirement. Do not retain prohibited media merely to preserve reproducibility.

Live cleanup uses request checks/sweeper, stream invalidation and bounded references. Restart can lose all sessions; optional local copies are labeled honestly. Clear/Delete cannot recall downloaded files or the clipboard and do not promise forensic memory erasure. End-review deadline edges, exact log retention and external storage locations remain explicit open decisions.
