# Team ownership

Hisham coordinates boundaries and final acceptance; module owners review implementation within their scope. Reviewer names below are team members, not invented GitHub identities. Consult a consumer when changing its input/output. Every directory README and [file catalogue](../architecture/file-catalog.md) names the accountable owner.

| Member | Owned paths and responsibilities | Required collaboration |
|---|---|---|
| Hisham | Root onboarding/contribution/agent rules; `docs/architecture/`, `docs/team/`, shared `tests/`, `scripts/`, `.github/`; integration, QA and release acceptance | Coordinates shared contracts, unresolved questions, scope, privacy wording and final demonstration |
| Basil | `data/`, `docs/datasets/`, dataset contract, stable semantic-label catalogue and model-to-data lineage | Receives model input requirements; supplies approved releases to Osama/Bavly, permitted fixtures/metadata to Ali and Adham |
| Osama | `ml/alphabet/`, `artifacts/alphabet/`, alphabet model card/configs/requirements/evidence and model-specific preprocessing | Basil for data; Ali for adapter/golden/runtime parity; Adham for approved letter framing; Hisham for scope |
| Bavly | `ml/words/`, `artifacts/words/`, temporal/neutral/completion specification, word model card/configs/requirements/evidence | Basil for sequences/boundaries; Ali for window/reset/gate/parity; Adham for manual fallback and framing; Hisham for capability approval |
| Ali | `backend/`, REST/WS/common adapter contracts, backend runtime/readiness/session/transcript/security behavior | Adham consumes APIs; model owners deliver predictors; Basil verifies lineage/labels; Hisham accepts integration |
| Adham | `frontend/`, screen/camera/controller/state/editor/recovery/copy/download/accessibility behavior | Ali agrees fields/versions; Basil and model owners approve public help/vocabulary and camera requirements |

`ml/common/` is jointly reviewed by Osama and Bavly, coordinated by Hisham. Add a shared utility only when input/output and behavior are actually identical and both owners accept it. `artifacts/` release policy belongs to Hisham/Ali with each model owner accountable for its scientific package. Contracts are central shared documents with the specific owner shown in each file, never a place for silent unilateral changes.

Directory ownership is accountability, not a separate repository or an automatic permission barrier. Teammates may make reviewed changes across boundaries with the affected owner/consumer. No CODEOWNERS file is fabricated without real GitHub identities. No automatic GitHub actions, commits, pushes, invitations or messages are created by this scaffold.
