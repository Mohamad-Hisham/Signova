# Complete file catalogue

Owner: Hisham. Application source placeholders remain comment-only with nine file-specific responsibility fields. The later CI task adds explicitly implemented repository tooling and tests, identified below. JSON and editor/Git metadata are explicitly distinguished from code. Original files retain their original bytes. Directory READMEs describe each folder, its inputs/outputs, consumers and prohibited contents.

| File | Owner | Status | Purpose |
|---|---|---|---|
| [.editorconfig](../../.editorconfig) | Hisham | configuration metadata | Editor-only UTF-8, line-ending and indentation conventions. |
| [.github/PULL_REQUEST_TEMPLATE.md](../../.github/PULL_REQUEST_TEMPLATE.md) | Hisham | documentation | PR review prompts for purpose, module, interfaces, dependencies, evidence, contract impact and reviewer. |
| [.github/README.md](../../.github/README.md) | Hisham | documentation | Directory guide for .github: contents, ownership, inputs, outputs, consumers and exclusions. |
| [.github/workflows/README.md](../../.github/workflows/README.md) | Hisham with Adham/Ali/model-owner input | documentation | Directory guide for .github/workflows: contents, ownership, inputs, outputs, consumers and exclusions. |
| [.github/workflows/ci.yml](../../.github/workflows/ci.yml) | Hisham | implemented CI workflow | Read-only push, combined-main PR, post-merge, merge-group and manual repository checks. |
| [.gitignore](../../.gitignore) | Hisham; Basil and model owners review content exceptions | Git safety configuration | Prevent secrets, local environments, restricted media, dataset payloads and large model artifacts entering Git. |
| [CONTRIBUTING.md](../../CONTRIBUTING.md) | Hisham | documentation | Simple contribution process, review duties and evidence rules for all six teammates. |
| [LICENSE](../../LICENSE) | Existing repository owner | original, unchanged | Original license preserved byte for byte; does not grant external data/model rights. |
| [README.md](../../README.md) | Hisham | original, unchanged | Original project-title README preserved byte for byte; detailed onboarding is START-HERE.md. |
| [START-HERE.md](../../START-HERE.md) | Hisham | documentation | Detailed root onboarding while preserving the existing README and source documents. |
| [Signova - Adham Frontend Engineering Handbook.docx](../../Signova%20-%20Adham%20Frontend%20Engineering%20Handbook.docx) | Adham source reference | original, unchanged | Original complete frontend handbook preserved; latest request overrides tutorial implementation instructions. |
| [Signova - Ali Backend Engineering Handbook.docx](../../Signova%20-%20Ali%20Backend%20Engineering%20Handbook.docx) | Ali source reference | original, unchanged | Original complete backend handbook preserved; exact contracts transcribed into shared docs. |
| [Signova - Basil Data Engineering Handbook.docx](../../Signova%20-%20Basil%20Data%20Engineering%20Handbook.docx) | Basil source reference | original, unchanged | Original complete data lifecycle handbook preserved; offline release/governance requirements reviewed. |
| [Signova - Osama Alphabet Model Engineering Handbook.docx](../../Signova%20-%20Osama%20Alphabet%20Model%20Engineering%20Handbook.docx) | Osama source reference | original, unchanged | Original complete alphabet handbook preserved; representation/evaluation/release responsibilities reviewed. |
| [Signova - Pavly Word Model Engineering Handbook.docx](../../Signova%20-%20Pavly%20Word%20Model%20Engineering%20Handbook.docx) | Bavly source reference; original filename retained | original, unchanged | Original complete word handbook preserved; temporal/live-window/boundary/release requirements reviewed. |
| [Signova.excalidraw](../../Signova.excalidraw) | Hisham source archive | original, unchanged | Original board preserved; all text, connectors and six images reviewed as earlier planning evidence. |
| [artifacts/README.md](../../artifacts/README.md) | Hisham and Ali coordinate; model owners own scientific releases | documentation | Directory guide for artifacts: contents, ownership, inputs, outputs, consumers and exclusions. |
| [artifacts/alphabet/README.md](../../artifacts/alphabet/README.md) | Osama; Ali verifies runtime acceptance | documentation | Directory guide for artifacts/alphabet: contents, ownership, inputs, outputs, consumers and exclusions. |
| [artifacts/alphabet/RELEASE-TEMPLATE.md](../../artifacts/alphabet/RELEASE-TEMPLATE.md) | Osama | documentation | Model-specific complete release checklist and future immutable external reference format without fake artifacts. |
| [artifacts/words/README.md](../../artifacts/words/README.md) | Bavly; Ali verifies runtime acceptance | documentation | Directory guide for artifacts/words: contents, ownership, inputs, outputs, consumers and exclusions. |
| [artifacts/words/RELEASE-TEMPLATE.md](../../artifacts/words/RELEASE-TEMPLATE.md) | Bavly | documentation | Model-specific complete release checklist and future immutable external reference format without fake artifacts. |
| [backend/.env.example](../../backend/.env.example) | Ali | comment-only placeholder | Describe future server-only runtime settings without active assignments or secrets. |
| [backend/README.md](../../backend/README.md) | Ali | documentation | Directory guide for backend: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/app/README.md](../../backend/app/README.md) | Ali | documentation | Directory guide for backend/app: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/app/api/README.md](../../backend/app/api/README.md) | Ali | documentation | Directory guide for backend/app/api: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/app/api/catalog.py](../../backend/app/api/catalog.py) | Ali | comment-only placeholder | Reserve public /api/v1/models and /api/v1/vocabulary REST boundaries. |
| [backend/app/api/health.py](../../backend/app/api/health.py) | Ali | comment-only placeholder | Reserve public /api/v1/health/live and /health/ready REST boundaries. |
| [backend/app/api/sessions.py](../../backend/app/api/sessions.py) | Ali | comment-only placeholder | Reserve REST create/read/capture/confirm/space/end/delete session boundaries. |
| [backend/app/api/transcript.py](../../backend/app/api/transcript.py) | Ali | comment-only placeholder | Reserve replacement, clear and current-revision TXT export REST boundaries. |
| [backend/app/config.py](../../backend/app/config.py) | Ali | comment-only placeholder | Reserve typed runtime settings and validated startup policy. |
| [backend/app/main.py](../../backend/app/main.py) | Ali | comment-only placeholder | Reserve the one FastAPI application composition and lifecycle boundary. |
| [backend/app/models/README.md](../../backend/app/models/README.md) | Ali; Osama/Bavly review their adapters | documentation | Directory guide for backend/app/models: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/app/models/alphabet.py](../../backend/app/models/alphabet.py) | Ali | comment-only placeholder | Reserve the dedicated Osama alphabet runtime adapter. |
| [backend/app/models/base.py](../../backend/app/models/base.py) | Ali | comment-only placeholder | Reserve Ali common adapter evidence and runtime lifecycle interface. |
| [backend/app/models/fake.py](../../backend/app/models/fake.py) | Ali | comment-only placeholder | Reserve an explicitly labeled deterministic development adapter for later software integration. |
| [backend/app/models/word.py](../../backend/app/models/word.py) | Ali | comment-only placeholder | Reserve the dedicated Bavly temporal word runtime adapter. |
| [backend/app/schemas/README.md](../../backend/app/schemas/README.md) | Ali with Adham consumer review | documentation | Directory guide for backend/app/schemas: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/app/schemas/common.py](../../backend/app/schemas/common.py) | Ali | comment-only placeholder | Reserve canonical Session, Transcript, Item, Candidate and safe Error response shapes. |
| [backend/app/schemas/events.py](../../backend/app/schemas/events.py) | Ali | comment-only placeholder | Reserve all protocol v1 client messages, server envelopes and event data objects. |
| [backend/app/schemas/rest.py](../../backend/app/schemas/rest.py) | Ali | comment-only placeholder | Reserve strict REST creation, capture, confirm, space, replacement, clear and end input schemas. |
| [backend/app/services/README.md](../../backend/app/services/README.md) | Ali | documentation | Directory guide for backend/app/services: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/app/services/commands.py](../../backend/app/services/commands.py) | Ali | comment-only placeholder | Reserve shared revision/state-version and bounded idempotency coordination. |
| [backend/app/services/recognition.py](../../backend/app/services/recognition.py) | Ali | comment-only placeholder | Reserve bounded sample admission, model routing and current candidate/segment orchestration. |
| [backend/app/services/sessions.py](../../backend/app/services/sessions.py) | Ali | comment-only placeholder | Reserve authoritative temporary RAM session and capability lifecycle. |
| [backend/app/services/transcript.py](../../backend/app/services/transcript.py) | Ali | comment-only placeholder | Reserve authoritative temporary confirmed transcript validation and atomic snapshots. |
| [backend/app/services/word_gate.py](../../backend/app/services/word_gate.py) | Ali | comment-only placeholder | Reserve deterministic word stability, evaluated release and segment-latch state transitions. |
| [backend/app/utilities/README.md](../../backend/app/utilities/README.md) | Ali | documentation | Directory guide for backend/app/utilities: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/app/utilities/errors.py](../../backend/app/utilities/errors.py) | Ali | comment-only placeholder | Reserve safe uniform REST/WS failure construction and redaction conventions. |
| [backend/app/utilities/ids.py](../../backend/app/utilities/ids.py) | Ali | comment-only placeholder | Reserve distinct opaque IDs, command UUID validation and cryptographically random session-secret helpers. |
| [backend/app/utilities/time.py](../../backend/app/utilities/time.py) | Ali | comment-only placeholder | Reserve separate monotonic deadline/stability timing and UTC display timestamps. |
| [backend/app/ws/README.md](../../backend/app/ws/README.md) | Ali | documentation | Directory guide for backend/app/ws: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/app/ws/live.py](../../backend/app/ws/live.py) | Ali | comment-only placeholder | Reserve the single authenticated /api/v1/ws/sessions/{sid} connection boundary. |
| [backend/requirements.in](../../backend/requirements.in) | Ali | comment-only placeholder | Reserve direct dependency intent for the single backend runtime. |
| [backend/requirements.lock.txt](../../backend/requirements.lock.txt) | Ali | comment-only placeholder | Reserve a tested dependency lock for the single backend runtime. |
| [backend/tests/README.md](../../backend/tests/README.md) | Ali | documentation | Directory guide for backend/tests: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/tests/fixtures/README.md](../../backend/tests/fixtures/README.md) | Ali with Basil permission review | documentation | Directory guide for backend/tests/fixtures: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/tests/integration/README.md](../../backend/tests/integration/README.md) | Ali | documentation | Directory guide for backend/tests/integration: contents, ownership, inputs, outputs, consumers and exclusions. |
| [backend/tests/unit/README.md](../../backend/tests/unit/README.md) | Ali | documentation | Directory guide for backend/tests/unit: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/README.md](../../data/README.md) | Basil | documentation | Directory guide for data: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/configs/README.md](../../data/configs/README.md) | Basil | documentation | Directory guide for data/configs: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/features/.gitkeep](../../data/features/.gitkeep) | Basil | empty directory marker | Empty marker retained alongside the payload-area README; stores no data. |
| [data/features/README.md](../../data/features/README.md) | Basil | documentation | Directory guide for data/features: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/interim/.gitkeep](../../data/interim/.gitkeep) | Basil | empty directory marker | Empty marker retained alongside the payload-area README; stores no data. |
| [data/interim/README.md](../../data/interim/README.md) | Basil | documentation | Directory guide for data/interim: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/labels/README.md](../../data/labels/README.md) | Basil | documentation | Directory guide for data/labels: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/manifests/README.md](../../data/manifests/README.md) | Basil | documentation | Directory guide for data/manifests: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/processed/.gitkeep](../../data/processed/.gitkeep) | Basil | empty directory marker | Empty marker retained alongside the payload-area README; stores no data. |
| [data/processed/README.md](../../data/processed/README.md) | Basil | documentation | Directory guide for data/processed: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/raw/.gitkeep](../../data/raw/.gitkeep) | Basil | empty directory marker | Empty marker retained alongside the payload-area README; stores no data. |
| [data/raw/README.md](../../data/raw/README.md) | Basil | documentation | Directory guide for data/raw: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/reports/DATA_CARD.md](../../data/reports/DATA_CARD.md) | Basil | documentation | Unfilled data card/audit/lineage template tied to the handbook full offline lifecycle. |
| [data/reports/README.md](../../data/reports/README.md) | Basil | documentation | Directory guide for data/reports: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/requirements.in](../../data/requirements.in) | Basil | comment-only placeholder | Reserve direct dependency intent for offline data engineering. |
| [data/requirements.lock.txt](../../data/requirements.lock.txt) | Basil | comment-only placeholder | Reserve a tested dependency lock for offline data reproducibility. |
| [data/scripts/README.md](../../data/scripts/README.md) | Basil | documentation | Directory guide for data/scripts: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/scripts/build_manifests.py](../../data/scripts/build_manifests.py) | Basil | comment-only placeholder | Reserve stable sample/asset/annotation and safe release manifest assembly. |
| [data/scripts/clean.py](../../data/scripts/clean.py) | Basil | comment-only placeholder | Reserve source-preserving reviewed photo/video cleaning and quarantine. |
| [data/scripts/inventory.py](../../data/scripts/inventory.py) | Basil | comment-only placeholder | Reserve source intake and photo/video inventory without altering originals. |
| [data/scripts/package_release.py](../../data/scripts/package_release.py) | Basil | comment-only placeholder | Reserve immutable directly usable alphabet/word data-release packaging and lineage references. |
| [data/scripts/split.py](../../data/scripts/split.py) | Basil | comment-only placeholder | Reserve deterministic signer/session/parent/duplicate-aware split assignment. |
| [data/scripts/validate_release.py](../../data/scripts/validate_release.py) | Basil | comment-only placeholder | Reserve hard dataset release checks and receiver compatibility validation. |
| [data/source_register/README.md](../../data/source_register/README.md) | Basil | documentation | Directory guide for data/source_register: contents, ownership, inputs, outputs, consumers and exclusions. |
| [data/tests/README.md](../../data/tests/README.md) | Basil | documentation | Directory guide for data/tests: contents, ownership, inputs, outputs, consumers and exclusions. |
| [docs/README.md](../../docs/README.md) | Hisham; document-specific owners named inside | documentation | Directory guide for docs: contents, ownership, inputs, outputs, consumers and exclusions. |
| [docs/architecture/README.md](../../docs/architecture/README.md) | Hisham | documentation | Directory guide for docs/architecture: contents, ownership, inputs, outputs, consumers and exclusions. |
| [docs/architecture/file-catalog.md](../../docs/architecture/file-catalog.md) | Hisham | documentation | Complete per-file owner, purpose and placeholder/original status inventory. |
| [docs/architecture/monorepo-structure.md](../../docs/architecture/monorepo-structure.md) | Hisham | documentation | Directory dependency rules and every meaningful deviation from the requested/handbook layouts. |
| [docs/architecture/repository-tree.md](../../docs/architecture/repository-tree.md) | Hisham | documentation | Complete project file tree including all original references and new scaffold files. |
| [docs/architecture/runtime-data-flow.md](../../docs/architecture/runtime-data-flow.md) | Hisham with Ali and Adham | documentation | Live sampling, REST/WebSocket sequence, candidate/commit distinction and transcript lifecycle diagrams. |
| [docs/architecture/system-overview.md](../../docs/architecture/system-overview.md) | Hisham | documentation | System context, modular monorepo components, model integration and scope boundaries with diagrams. |
| [docs/contracts/README.md](../../docs/contracts/README.md) | Ali coordinates runtime contracts; Basil dataset/vocabulary; model owners their semantics; Adham browser review | documentation | Directory guide for docs/contracts: contents, ownership, inputs, outputs, consumers and exclusions. |
| [docs/contracts/frontend-backend-contract.md](../../docs/contracts/frontend-backend-contract.md) | Ali and Adham with Hisham acceptance | documentation | Screen/control duties, authority, version merging, camera cleanup, recovery and exact user-visible failure behavior. |
| [docs/contracts/model-interface.md](../../docs/contracts/model-interface.md) | Ali, Osama, Bavly and Basil | documentation | Separate model representations, common adapter evidence, release deliverables and scientific/runtime acceptance. |
| [docs/contracts/rest-api.md](../../docs/contracts/rest-api.md) | Ali with Adham review | documentation | Exact REST routes, fields, access, status codes, mutation semantics, retries and failures from both handbooks. |
| [docs/contracts/starting-limits.md](../../docs/contracts/starting-limits.md) | Ali with Hisham approval and consumer review | documentation | Explicitly label all handbook limits and targets as initial settings requiring model and hardware verification. |
| [docs/contracts/vocabulary-contract.md](../../docs/contracts/vocabulary-contract.md) | Basil; model owners, Ali and Adham share boundary review | documentation | Stable semantic IDs, Arabic/public field mappings, class order and unresolved approved English distribution. |
| [docs/contracts/websocket-protocol.md](../../docs/contracts/websocket-protocol.md) | Ali with Adham review | documentation | Exact WebSocket URL, handshake, envelopes, all client/server message fields and flow-control/close semantics. |
| [docs/datasets/README.md](../../docs/datasets/README.md) | Basil with Hisham review | documentation | Directory guide for docs/datasets: contents, ownership, inputs, outputs, consumers and exclusions. |
| [docs/datasets/data-governance.md](../../docs/datasets/data-governance.md) | Basil with Hisham, Ali, Adham and model-owner review | documentation | Separate storage domains, Git safety, authorized offline releases, live privacy and withdrawal responsibilities. |
| [docs/datasets/source-register.md](../../docs/datasets/source-register.md) | Basil | documentation | Traceable but explicitly unverified candidate datasets from the board and the required source-audit fields. |
| [docs/guides/Signova-Backend-Guide.pdf](../../docs/guides/Signova-Backend-Guide.pdf) | Hisham and Basel | documentation | Backend handover, local setup and integration plan. |
| [docs/runbooks/README.md](../../docs/runbooks/README.md) | Hisham coordinates; module owners maintain their operational instructions | documentation | Directory guide for docs/runbooks: contents, ownership, inputs, outputs, consumers and exclusions. |
| [docs/runbooks/continuous-integration.md](../../docs/runbooks/continuous-integration.md) | Hisham | documentation | Local commands, event/revision behavior, hosted success/failure tests and main required-check setup. |
| [docs/runbooks/integration-checklist.md](../../docs/runbooks/integration-checklist.md) | Hisham | documentation | Future cross-module acceptance matrix separating software correctness, scientific evidence and current scaffold status. |
| [docs/team/README.md](../../docs/team/README.md) | Hisham | documentation | Directory guide for docs/team: contents, ownership, inputs, outputs, consumers and exclusions. |
| [docs/team/git-workflow.md](../../docs/team/git-workflow.md) | Hisham | documentation | Issue-to-branch-to-review-to-main workflow with clear contract and Git-safety responsibilities. |
| [docs/team/handoffs.md](../../docs/team/handoffs.md) | Hisham with all module owners | documentation | Diagram and concrete producer/receiver contents, acceptance and defect-routing for all six teammates. |
| [docs/team/meeting-rhythm.md](../../docs/team/meeting-rhythm.md) | Hisham | documentation | Confirmed final date, explicitly unconfirmed Tuesday start and evidence-focused coordination rhythm. |
| [docs/team/ownership.md](../../docs/team/ownership.md) | Hisham | documentation | All six members, exact owned paths and cross-module reviewer/consumer responsibilities. |
| [frontend/.env.example](../../frontend/.env.example) | Adham | comment-only placeholder | Describe future public API/WS base URL settings without assigning or storing secrets. |
| [frontend/README.md](../../frontend/README.md) | Adham | documentation | Directory guide for frontend: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/e2e/README.md](../../frontend/e2e/README.md) | Adham with Ali and Hisham | documentation | Directory guide for frontend/e2e: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/index.html](../../frontend/index.html) | Adham | comment-only placeholder | Reserve the future accessible HTML document and single browser mount point. |
| [frontend/package.json](../../frontend/package.json) | Adham | minimal JSON metadata | Minimal valid project identity only; no dependencies, scripts, runnable entrypoint or lock claims. |
| [frontend/src/README.md](../../frontend/src/README.md) | Adham | documentation | Directory guide for frontend/src: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/api/README.md](../../frontend/src/api/README.md) | Adham with Ali contract review | documentation | Directory guide for frontend/src/api: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/api/client.ts](../../frontend/src/api/client.ts) | Adham | comment-only placeholder | Provide the future native Fetch boundary for the exact REST v1 catalogue. |
| [frontend/src/api/contracts.ts](../../frontend/src/api/contracts.ts) | Adham | comment-only placeholder | Mirror approved public REST/WS types and selected Zod runtime validation. |
| [frontend/src/api/liveSocket.ts](../../frontend/src/api/liveSocket.ts) | Adham | comment-only placeholder | Own the future native WebSocket transport lifecycle and v1 envelope dispatch. |
| [frontend/src/app/App.tsx](../../frontend/src/app/App.tsx) | Adham | comment-only placeholder | Compose Homepage, Live Translator, Sign Library, About/Help and terminal/recovery surfaces. |
| [frontend/src/app/README.md](../../frontend/src/app/README.md) | Adham | documentation | Directory guide for frontend/src/app: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/app/sessionController.ts](../../frontend/src/app/sessionController.ts) | Adham | comment-only placeholder | Own a single session side-effect lifecycle across REST, socket and camera. |
| [frontend/src/app/sessionReducer.ts](../../frontend/src/app/sessionReducer.ts) | Adham | comment-only placeholder | Define serializable browser state transitions without losing confirmed text or dirty drafts. |
| [frontend/src/camera/README.md](../../frontend/src/camera/README.md) | Adham | documentation | Directory guide for frontend/src/camera: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/camera/frameSampler.ts](../../frontend/src/camera/frameSampler.ts) | Adham | comment-only placeholder | Encode bounded unmirrored JPEG samples with one-in-flight flow control. |
| [frontend/src/camera/useCamera.ts](../../frontend/src/camera/useCamera.ts) | Adham | comment-only placeholder | Own one video-only permission request and its actual media tracks. |
| [frontend/src/components/ConfirmDialog.tsx](../../frontend/src/components/ConfirmDialog.tsx) | Adham | comment-only placeholder | Provide accessible deliberate confirmation for meaningful removal/navigation actions. |
| [frontend/src/components/README.md](../../frontend/src/components/README.md) | Adham | documentation | Directory guide for frontend/src/components: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/components/StatusMessage.tsx](../../frontend/src/components/StatusMessage.tsx) | Adham | comment-only placeholder | Present reusable safe status and error guidance without noisy private diagnostics. |
| [frontend/src/features/README.md](../../frontend/src/features/README.md) | Adham | documentation | Directory guide for frontend/src/features: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/features/about-help/AboutHelp.tsx](../../frontend/src/features/about-help/AboutHelp.tsx) | Adham | comment-only placeholder | Explain Signova scope, camera permissions, supported signs, segmentation and temporary storage. |
| [frontend/src/features/about-help/README.md](../../frontend/src/features/about-help/README.md) | Adham | documentation | Directory guide for frontend/src/features/about-help: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/features/home/HomePage.tsx](../../frontend/src/features/home/HomePage.tsx) | Adham | comment-only placeholder | Present Homepage mode selection, readiness and temporary-data/recovery choices. |
| [frontend/src/features/home/README.md](../../frontend/src/features/home/README.md) | Adham | documentation | Directory guide for frontend/src/features/home: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/features/recognition/README.md](../../frontend/src/features/recognition/README.md) | Adham | documentation | Directory guide for frontend/src/features/recognition: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/features/recognition/RecognitionPreview.tsx](../../frontend/src/features/recognition/RecognitionPreview.tsx) | Adham | comment-only placeholder | Display only current candidate evidence and Confirm eligibility. |
| [frontend/src/features/recognition/RecognitionWorkspace.tsx](../../frontend/src/features/recognition/RecognitionWorkspace.tsx) | Adham | comment-only placeholder | Compose Live Translator camera, candidate, confirmed transcript and session controls. |
| [frontend/src/features/recovery/README.md](../../frontend/src/features/recovery/README.md) | Adham | documentation | Directory guide for frontend/src/features/recovery: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/features/recovery/RecoveryView.tsx](../../frontend/src/features/recovery/RecoveryView.tsx) | Adham | comment-only placeholder | Explain reconnection, expiry and recovered local copy without claiming active server state. |
| [frontend/src/features/recovery/recoveryStore.ts](../../frontend/src/features/recovery/recoveryStore.ts) | Adham | comment-only placeholder | Manage explicitly opted-in bounded tab recovery without restoring removed content. |
| [frontend/src/features/sign-library/README.md](../../frontend/src/features/sign-library/README.md) | Adham | documentation | Directory guide for frontend/src/features/sign-library: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/features/sign-library/SignLibrary.tsx](../../frontend/src/features/sign-library/SignLibrary.tsx) | Adham | comment-only placeholder | Browse/search the model-compatible supported signs and permitted examples. |
| [frontend/src/features/transcript/README.md](../../frontend/src/features/transcript/README.md) | Adham | documentation | Directory guide for frontend/src/features/transcript: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/features/transcript/TranscriptEditor.tsx](../../frontend/src/features/transcript/TranscriptEditor.tsx) | Adham | comment-only placeholder | Edit a separate paused transcript draft using the base server revision. |
| [frontend/src/features/transcript/TranscriptPanel.tsx](../../frontend/src/features/transcript/TranscriptPanel.tsx) | Adham | comment-only placeholder | Render canonical confirmed transcript and available text actions. |
| [frontend/src/features/transcript/transcriptActions.ts](../../frontend/src/features/transcript/transcriptActions.ts) | Adham | comment-only placeholder | Own explicit browser clipboard and local/authorized-server TXT download interactions. |
| [frontend/src/main.tsx](../../frontend/src/main.tsx) | Adham | comment-only placeholder | Future browser entrypoint and React root ownership. |
| [frontend/src/mocks/README.md](../../frontend/src/mocks/README.md) | Adham with Ali schema review | documentation | Directory guide for frontend/src/mocks: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/mocks/SCENARIOS.md](../../frontend/src/mocks/SCENARIOS.md) | Adham with Ali | documentation | Future deterministic synthetic browser transport cases without implementing a fake service or fixtures. |
| [frontend/src/styles/README.md](../../frontend/src/styles/README.md) | Adham | documentation | Directory guide for frontend/src/styles: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/src/styles/global.css](../../frontend/src/styles/global.css) | Adham | comment-only placeholder | Reserve global responsive, RTL/LTR, focus and plain-text layout behavior. |
| [frontend/src/styles/tokens.css](../../frontend/src/styles/tokens.css) | Adham | comment-only placeholder | Reserve consistent accessible visual tokens for Signova UI. |
| [frontend/tests/README.md](../../frontend/tests/README.md) | Adham | documentation | Directory guide for frontend/tests: contents, ownership, inputs, outputs, consumers and exclusions. |
| [frontend/tsconfig.json](../../frontend/tsconfig.json) | Adham | empty JSON configuration placeholder | Valid empty JSON placeholder; future compiler/JSX/strictness options are documented in frontend README. |
| [frontend/vite.config.ts](../../frontend/vite.config.ts) | Adham | comment-only placeholder | Reserve future Vite development/build and test-compatible configuration. |
| [ml/README.md](../../ml/README.md) | Osama and Bavly; Hisham coordinates boundaries | documentation | Directory guide for ml: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/alphabet/README.md](../../ml/alphabet/README.md) | Osama | documentation | Directory guide for ml/alphabet: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/alphabet/configs/README.md](../../ml/alphabet/configs/README.md) | Osama | documentation | Directory guide for ml/alphabet/configs: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/alphabet/reports/MODEL_CARD.md](../../ml/alphabet/reports/MODEL_CARD.md) | Osama | documentation | Unfilled scientific model card with task-specific live capability and evidence requirements. |
| [ml/alphabet/reports/README.md](../../ml/alphabet/reports/README.md) | Osama | documentation | Directory guide for ml/alphabet/reports: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/alphabet/requirements.in](../../ml/alphabet/requirements.in) | Osama | comment-only placeholder | Reserve direct dependency intent for alphabet model development. |
| [ml/alphabet/requirements.lock.txt](../../ml/alphabet/requirements.lock.txt) | Osama | comment-only placeholder | Reserve a tested dependency lock for alphabet reproducibility. |
| [ml/alphabet/src/README.md](../../ml/alphabet/src/README.md) | Osama | documentation | Directory guide for ml/alphabet/src: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/alphabet/src/dataset.py](../../ml/alphabet/src/dataset.py) | Osama | comment-only placeholder | Reserve the alphabet model-specific loader for Basil approved immutable releases. |
| [ml/alphabet/src/decision.py](../../ml/alphabet/src/decision.py) | Osama | comment-only placeholder | Reserve the alphabet classifier rejection/calibration and neutral-capability policy. |
| [ml/alphabet/src/evaluate.py](../../ml/alphabet/src/evaluate.py) | Osama | comment-only placeholder | Reserve alphabet scientific evaluation, rejection coverage and target-runtime benchmarks. |
| [ml/alphabet/src/model.py](../../ml/alphabet/src/model.py) | Osama | comment-only placeholder | Reserve the independent alphabet model architecture definition used by training and inference. |
| [ml/alphabet/src/predict.py](../../ml/alphabet/src/predict.py) | Osama | comment-only placeholder | Reserve side-effect-free alphabet inference from a trusted frozen release. |
| [ml/alphabet/src/preprocessing.py](../../ml/alphabet/src/preprocessing.py) | Osama | comment-only placeholder | Reserve the exact deterministic alphabet training-evaluation-serving input recipe. |
| [ml/alphabet/src/train.py](../../ml/alphabet/src/train.py) | Osama | comment-only placeholder | Reserve offline alphabet training and controlled validation checkpoint selection. |
| [ml/alphabet/tests/README.md](../../ml/alphabet/tests/README.md) | Osama | documentation | Directory guide for ml/alphabet/tests: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/common/README.md](../../ml/common/README.md) | Osama and Bavly jointly; Hisham coordinates | documentation | Directory guide for ml/common: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/common/contracts/README.md](../../ml/common/contracts/README.md) | Osama and Bavly jointly | documentation | Directory guide for ml/common/contracts: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/common/evaluation/README.md](../../ml/common/evaluation/README.md) | Osama and Bavly jointly | documentation | Directory guide for ml/common/evaluation: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/common/preprocessing/README.md](../../ml/common/preprocessing/README.md) | Osama and Bavly jointly | documentation | Directory guide for ml/common/preprocessing: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/words/README.md](../../ml/words/README.md) | Bavly | documentation | Directory guide for ml/words: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/words/configs/README.md](../../ml/words/configs/README.md) | Bavly | documentation | Directory guide for ml/words/configs: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/words/reports/MODEL_CARD.md](../../ml/words/reports/MODEL_CARD.md) | Bavly | documentation | Unfilled scientific model card with task-specific live capability and evidence requirements. |
| [ml/words/reports/README.md](../../ml/words/reports/README.md) | Bavly | documentation | Directory guide for ml/words/reports: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/words/requirements.in](../../ml/words/requirements.in) | Bavly | comment-only placeholder | Reserve direct dependency intent for word model development. |
| [ml/words/requirements.lock.txt](../../ml/words/requirements.lock.txt) | Bavly | comment-only placeholder | Reserve a tested dependency lock for word reproducibility. |
| [ml/words/src/README.md](../../ml/words/src/README.md) | Bavly | documentation | Directory guide for ml/words/src: contents, ownership, inputs, outputs, consumers and exclusions. |
| [ml/words/src/dataset.py](../../ml/words/src/dataset.py) | Bavly | comment-only placeholder | Reserve the word model-specific loader for Basil approved immutable releases. |
| [ml/words/src/decision.py](../../ml/words/src/decision.py) | Bavly | comment-only placeholder | Reserve the word classifier rejection/calibration and neutral-capability policy. |
| [ml/words/src/evaluate.py](../../ml/words/src/evaluate.py) | Bavly | comment-only placeholder | Reserve word scientific evaluation, rejection coverage and target-runtime benchmarks. |
| [ml/words/src/export.py](../../ml/words/src/export.py) | Bavly | comment-only placeholder | Reserve optional word inference export and complete versioned package assembly. |
| [ml/words/src/model.py](../../ml/words/src/model.py) | Bavly | comment-only placeholder | Reserve the independent word model architecture definition used by training and inference. |
| [ml/words/src/predict.py](../../ml/words/src/predict.py) | Bavly | comment-only placeholder | Reserve side-effect-free word inference from a trusted frozen release. |
| [ml/words/src/preprocessing.py](../../ml/words/src/preprocessing.py) | Bavly | comment-only placeholder | Reserve the exact deterministic word training-evaluation-serving input recipe. |
| [ml/words/src/train.py](../../ml/words/src/train.py) | Bavly | comment-only placeholder | Reserve offline word training and controlled validation checkpoint selection. |
| [ml/words/tests/README.md](../../ml/words/tests/README.md) | Bavly | documentation | Directory guide for ml/words/tests: contents, ownership, inputs, outputs, consumers and exclusions. |
| [scripts/README.md](../../scripts/README.md) | Hisham; relevant module owner reviews future helpers | documentation | Directory guide for scripts: contents, ownership, inputs, outputs, consumers and exclusions. |
| [scripts/check_repository.py](../../scripts/check_repository.py) | Hisham | implemented CI tooling | Standard-library syntax, strict JSON, inline local link, module-guide and Git ignore validation. |
| [tests/README.md](../../tests/README.md) | Hisham; producer/consumer owners supply acceptance evidence | documentation | Directory guide for tests: contents, ownership, inputs, outputs, consumers and exclusions. |
| [tests/ci/README.md](../../tests/ci/README.md) | Hisham | documentation | CI-tooling test ownership, synthetic inputs, invocation and excluded application/data scope. |
| [tests/ci/test_repository_checks.py](../../tests/ci/test_repository_checks.py) | Hisham | implemented CI tooling tests | Regression tests for valid inputs, broken syntax/JSON/links and ignored-file handling in temporary Git checkouts. |
| [tests/contracts/README.md](../../tests/contracts/README.md) | Hisham coordinates Ali/Adham and model/data owners | documentation | Directory guide for tests/contracts: contents, ownership, inputs, outputs, consumers and exclusions. |
| [tests/fixtures/README.md](../../tests/fixtures/README.md) | Hisham with Basil permission review and owning producer | documentation | Directory guide for tests/fixtures: contents, ownership, inputs, outputs, consumers and exclusions. |
| [tests/integration/README.md](../../tests/integration/README.md) | Hisham with Ali/Adham and model owners | documentation | Directory guide for tests/integration: contents, ownership, inputs, outputs, consumers and exclusions. |
