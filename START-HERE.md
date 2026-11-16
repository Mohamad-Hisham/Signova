# Signova: start here

Signova will recognize supported Arabic Sign Language letters and isolated words from a webcam and display Arabic and approved English equivalents. Application source is still a comment-only scaffold and cannot run, build, infer or train yet. Repository CI/checker tooling has been implemented under a later authorized task and needs no project dependencies. No application dependencies or usable application lockfiles have been installed or generated.

The existing root README, license, five handbooks, and Excalidraw board are preserved byte for byte. This entry point provides the detailed onboarding that would normally live in the root README. The current workspace is already the repository root; no second nested `signova/` repository is created.

## Start with the contracts

Read [the system overview](docs/architecture/system-overview.md), [runtime flows](docs/architecture/runtime-data-flow.md), [ownership](docs/team/ownership.md), and [open decisions](docs/architecture/decisions/open-questions.md). Then read your module README and the relevant contracts under [docs/contracts](docs/contracts/README.md).

One React/TypeScript/Vite frontend communicates through native Fetch and WebSocket with one Python 3.11-target FastAPI backend. The backend loads independent alphabet and word packages through dedicated adapters. Basil's offline data releases feed the two model owners; approved versioned model releases reach Ali through external artifact storage. These are modules in one monorepo, not microservices.

The live path is browser camera → bounded unmirrored JPEG samples → authenticated WebSocket → validation and server preprocessing → selected adapter → candidate preview → explicit confirmation → authoritative RAM transcript → browser snapshot. Automatic word completion requires evaluated release evidence and joint acceptance. Pause discards pending evidence; it never classifies a final buffered clip.

## Ownership

| Member | Primary responsibility | Start directory |
|---|---|---|
| Hisham | Architecture, integration, QA, shared contracts and final acceptance | `docs/`, `tests/`, root collaboration files |
| Basil | Rights, intake, cleaning, labels, groups/splits, dataset releases and lineage | `data/`, `docs/datasets/` |
| Osama | Alphabet model, its preprocessing, evaluation and release | `ml/alphabet/`, `artifacts/alphabet/` |
| Bavly | Word model, temporal requirements, boundary evidence and release | `ml/words/`, `artifacts/words/` |
| Ali | Backend, session capabilities, adapters, inference orchestration and transcript authority | `backend/` |
| Adham | Frontend, camera lifecycle, preview, transcript editor, copy/download and recovery UX | `frontend/` |

The package directory is `ml/words/`, but the public API mode is exactly `word`. Both models retain separate label maps, shapes, preprocessing and scientific acceptance.

## Product and retention boundaries

The planned surfaces are Homepage, Live Translator with Alphabet and Word modes, Recognition Preview, Confirmed Transcript with editing/copy/download/clear, Sign Library, and About/Help. Only confirmed backend items alter transcript text. English uses an approved mapping; the v1 wire schema currently lacks its delivery mechanism, which remains an explicit release decision.

Active sessions and confirmed transcripts exist temporarily in backend RAM. The browser renders snapshots and keeps drafts in tab memory. Opted-in tab recovery may use bounded `sessionStorage`; it is disabled by default. There is no database, Redis, account system, cloud transcript history, default recording, automatic training collection, unrestricted sentence translation, grammar generation, or ASL model. One backend process, one worker and one replica are required by the RAM design. Restart can destroy every active session.

## Where to go next

| Location | Contents |
|---|---|
| `docs/` | Architecture, exact REST/WebSocket contracts, model/data/vocabulary boundaries, decisions, team handoffs and runbooks |
| `frontend/` | Comment-only React/TypeScript/camera/network placeholders; minimal package metadata and empty valid TypeScript config |
| `backend/` | Comment-only FastAPI schema/route/service/adapter placeholders and dependency planning notes |
| `ml/` | Independent alphabet/word training, evaluation, prediction and export placeholders; narrowly scoped shared documentation |
| `data/` | Offline engineering metadata and script placeholders; ignored local payload areas |
| `artifacts/` | Model-release requirements, cards and external release references; no weights or fake releases |
| `tests/` | Implemented CI-tooling tests plus future shared contract/integration acceptance descriptions |
| `scripts/`, `.github/` | Repository checker, GitHub Actions workflow and pull-request template |

See the [complete repository tree](docs/architecture/repository-tree.md), [every-file catalogue](docs/architecture/file-catalog.md), [source review](docs/architecture/source-review.md), and [scaffold verification](docs/runbooks/scaffold-verification.md).

Final project deadline: **December 1, 2026**. Weekly meeting: Tuesday, **10:00 PM or 11:00 PM Cairo time**, exact start TBD. Historical handbook schedules are planning references, not evidence of completed work. Hisham must reconcile conflicting intermediate dates.

Application implementation requires a separately assigned task. Repository CI checks branch pushes, PR merge revisions targeting main and pushes to main after merging. Follow the [local checks and GitHub smoke tests](docs/runbooks/continuous-integration.md) before relying on the check. No application implementation, build, deployment, commit or push was performed by the CI authoring task.
