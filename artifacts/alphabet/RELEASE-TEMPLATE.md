# Signova alphabet release specification template

Producer: Osama. Receiver: Ali; Basil reviews lineage/permissions and Hisham scope/acceptance. Status: **specification only; no actual release/version/artifact/manifest exists here.** External storage location, actual versions/hashes and runtime/input facts are TBD.

A future immutable external release must contain model manifest, trusted weights or approved export, architecture where needed, callable predictor, exact preprocessing spec/implementation, ordered labels with stable IDs/Arabic text, frozen decision/rejection/calibration configuration, runtime requirements/lock, at least five small permitted golden fixtures with expected outcomes/tolerances, scientific evaluation, model card, integration/reset instructions and SHA-256 checksums. Training code is referenced by version/commit and is not imported by live inference.

The manifest declares its actual artifact/class-map/policy/fixture paths, model identity/version, format/framework/Python/provider/device, tensor names/dtype/shape/axes, orientation/color/crop/pad/normalization, data/split/label/recipe lineage, class-map hash, score/neutral definitions, checksums and supported capabilities. Specify reviewed static-versus-temporal classes, context/framing/handedness and any sequence/reset requirements; never assume 28 classes.

Example filenames in the source handbooks are not mandatory common names: alphabet may use classes.json/decision_policy.json/checksums.sha256 while words may use labels.json/decision.json/SHA256SUMS. No JSON placeholders or fake weights are created. Ali follows manifest-declared paths and verifies every approved file.

Publish only reviewed public-safe metadata, immutable external reference and real hashes under a future version directory here. Keep binary payloads and restricted fixtures in approved controlled storage. Do not replace bytes under an accepted version, put temporary download URLs with secrets in Git, or promote a package without fresh target-runtime/golden/parity acceptance. See the [model interface and release contract](../../docs/contracts/model-interface.md).

Future release-reference record: immutable model/version and artifact hash; source/code and dataset/split/label/recipe versions; approved storage reference without secret; runtime/capture/protocol compatibility; evaluation/card/checksum references; receiver/date/accepted capability; limitations and rollback version. Populate only with actual evidence, never examples presented as an accepted release.
