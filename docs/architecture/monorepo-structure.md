# Monorepo structure and dependency direction

Owner: Hisham. [The complete tree](repository-tree.md) lists every delivered file; [the file catalogue](file-catalog.md) gives its owner, purpose and scaffold status. Each directory README explains inputs, outputs, consumers and prohibited content. Each source placeholder documents its individual future behavior and acceptance checks.

| Module | Allowed dependencies | Outputs and consumers |
|---|---|---|
| `frontend/` | Browser APIs and `docs/contracts/` wire definitions | JPEG messages, explicit REST actions and user-facing snapshots |
| `backend/` | Contracts, approved inference packages and external artifact releases | Validation, candidates, authoritative temporary session/transcript snapshots |
| `ml/alphabet/` | Its own model/runtime/data recipe; genuinely shared `ml/common/` tools if needed | Osama's independent evaluated alphabet inference release |
| `ml/words/` | Its own temporal/model/runtime/data recipe; genuinely shared common tools if needed | Bavly's independent evaluated word inference release |
| `data/` | Authorized source storage and owner-approved input requirements | Basil's reproducible offline manifests, labels, splits and data releases |
| `artifacts/` | Model-owner release evidence and safe external references | Trusted immutable package specifications consumed by Ali |
| `docs/`, `tests/` | Agreed source references and safe synthetic/authorized evidence | Cross-module contracts and integration acceptance |

Frontend never imports backend Python, weights or ML/training code. Backend route handlers never train or directly own preprocessing experiments. API/WS → services → adapters → model predictors is the live direction. Models do not import backend routes or mutate transcripts. The alphabet and word implementations do not import each other. `ml/common/` is initially documentation-only because shared behavior has not yet been established; it must never force common dimensions or transforms.

## Structural adjustments and reasons

1. Use the existing workspace as the repository root instead of nesting a second `signova/`. This preserves the current Git repository and original inputs.
2. Preserve the existing `README.md` and `LICENSE`; add `START-HERE.md` as detailed root onboarding. Their pre-scaffold SHA-256 values are recorded in the source review. No original user file is replaced or moved.
3. Centralize handbook-local `docs/api.md`, `docs/ws.md`, `docs/model.md`, `docs/data_contract.md`, `docs/screens.md`, and runbook responsibilities under the requested `docs/contracts/`, `docs/architecture/` and `docs/runbooks/`. Do not create duplicate competing contract documents.
4. Use `backend/app/ws/live.py` rather than the handbook's earlier `backend/app/api/live.py`; its external URL remains exactly `/api/v1/ws/sessions/{sid}`. Central `artifacts/` replaces backend-local `model_artifacts/` and model-local `releases/`; no binary copies are embedded in source trees.
5. Standardize requested model source naming as `dataset.py` and `predict.py` rather than the tutorial's `data.py`/`inference.py`. Add separate `preprocessing.py` and `decision.py` placeholders so inference will not import training entrypoints and so trained recipes/rejection policies can be versioned explicitly. Architecture stays in `model.py`. No functions or packaging logic are supplied.
6. Add `frontend/src/main.tsx`, individual feature/UI placeholders, `styles/*.css`, and an `about-help/` feature to cover the actual screens without implementing them. Keep future tests at `frontend/tests/` and `frontend/e2e/`, rather than duplicating the tutorial's `src/tests/` location.
7. Keep `tsconfig.json` as a valid empty object and `package.json` as minimal metadata only. Their intended configuration is described in the frontend README; no dependencies, scripts, entrypoint tags or working build are supplied. Future JSON schemas are specified in Markdown, not invalid commented JSON files.
8. Add model-local dependency lock *placeholders* and Basil's `data/requirements.in`, `data/requirements.lock.txt`, `data/configs/`, `data/reports/`, `data/tests/` plus offline script placeholders. They serve the handbook's reproducibility/audit duties and are not tested locks, finished tooling or real release evidence.
9. Add `MODEL_CARD.md` templates and `RELEASE-TEMPLATE.md` specifications to distinguish scientific scope and complete model handoffs from weights alone. They are templates, never fake releases.
10. Add source review, exact starting-limit register, complete file catalogue/tree, scaffold verification, test acceptance READMEs and directory explanations. These provide traceability requested for beginner contributors. No extra service, database, Redis, container or deployment workflow is introduced.

Python packaging names and build metadata remain future owner decisions within these boundaries; comment-only files are not claimed to be installable packages. Dependencies must be tested together for live inference before locks or runtime compatibility are asserted.

## Later CI implementation

The separately authorized CI task adds `.github/workflows/ci.yml`,
`scripts/check_repository.py`, `tests/ci/` and the CI runbook. These are executable
repository tooling and regression tests. Earlier scaffold-only statements describe the
original application baseline. The checker accepts real Python syntax when application
implementation is later assigned; it does not freeze source as comments. Application
frontend/backend/model test suites are not yet available.
