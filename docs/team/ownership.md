# Team ownership

Hisham and Ali share backend ownership. Hisham coordinates boundaries and final acceptance; module owners review implementation within their scope. Reviewer names below are team members, not invented GitHub identities. Consult a consumer when changing its input/output. Every directory README and [file catalogue](../architecture/file-catalog.md) names the accountable owner.

| Member | Owned paths and responsibilities | Required collaboration |
|---|---|---|
| Hisham | Shared ownership of `backend/` with Ali. Leads live frame handling, recognition and model adapter implementation. Also owns root onboarding/contribution/agent rules; `docs/architecture/`, `docs/team/`, shared `tests/`, `scripts/`, `.github/`; integration, QA and release acceptance | Coordinates shared contracts, unresolved questions, scope, privacy wording and final demonstration |
| Basil | `data/`, `docs/datasets/`, dataset manifests, stable semantic-label catalogue and model-to-data lineage | Receives model input requirements; supplies approved releases to Osama/Bavly, permitted fixtures/metadata to Ali and Adham |
| Osama | `ml/alphabet/`, `artifacts/alphabet/`, alphabet model card/configs/requirements/evidence and model-specific preprocessing | Basil for data; Hisham and Ali for adapter and runtime parity; Adham for approved letter framing; Hisham for scope |
| Bavly | `ml/words/`, `artifacts/words/`, temporal/neutral/completion specification, word model card/configs/requirements/evidence | Basil for sequences/boundaries; Hisham and Ali for window, reset, gating and parity; Adham for manual fallback and framing; Hisham for capability approval |
| Ali | Shared ownership of `backend/` with Hisham. Leads REST, WebSocket and common adapter contracts, session and transcript behavior. | Adham reviews public API changes. Hisham and Ali coordinate runtime integration, readiness and security. |
| Adham | `frontend/`, screen/camera/controller/state/editor/recovery/copy/download/accessibility behavior | Ali agrees fields/versions; Basil and model owners approve public help/vocabulary and camera requirements |

Within `backend/app/`, Ali owns `api/`, `schemas/`, `main.py`, `config.py`, `utilities/` and the `sessions.py`, `commands.py` and `transcript.py` services. Hisham owns `ws/`, `models/`, `recognition.py` and `word_gate.py`. Use the [backend file catalogue](../architecture/file-catalog.md) for individual files.

`ml/common/` is jointly reviewed by Osama and Bavly, coordinated by Hisham. Add a shared utility only when input/output and behavior are actually identical and both owners accept it. `artifacts/` release policy belongs to Hisham/Ali with each model owner accountable for its scientific package. Contracts are central shared documents with the specific owner shown in each file, never a place for silent unilateral changes.

Directory ownership is accountability, not a separate repository or an automatic permission barrier. Teammates may make reviewed changes across boundaries with the affected owner/consumer. No CODEOWNERS file is fabricated without real GitHub identities. No automatic GitHub actions, commits, pushes, invitations or messages are created by this scaffold.
