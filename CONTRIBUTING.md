# Contributing to Signova

Read [START-HERE](START-HERE.md), [ownership](docs/team/ownership.md), [handoffs](docs/team/handoffs.md), and [the Git workflow](docs/team/git-workflow.md). Application source is still a scaffold. Repository CI/checker code and its tests are implemented. Application tests, commands and dependency locks will be added during explicitly assigned implementation work.

Use one issue with an accountable owner and acceptance criteria → feature branch → small change → pull request → peer review → relevant checks → merge into `main`. Keep `main` reserved for the integrated project structure; once implemented, it should stay reproducible. Work locally during this task without commits or pushes.

Branch examples are `feature/frontend-camera-lifecycle`, `docs/model-handoff`, or `fix/backend-revision-contract`; they are conventions, not existing branches. Name changes by module and behavior. The PR template requires purpose, module, input/output changes, dependencies, evidence, contract impact and reviewer.

Ali owns REST/WebSocket schemas; Adham reviews their browser impact. Osama and Bavly own their respective model/input semantics; Basil reviews data and label lineage; Hisham coordinates shared decisions and final acceptance. No teammate changes another module's contract silently. A contract change includes examples, failure behavior, affected consumers and migration/version impact before implementation is merged.

Keep private samples, tokens, transcripts, signer identities, source consent documents and large artifacts out of issues, fixtures and Git. Use synthetic descriptions or approved fixture IDs with restricted evidence stored separately. Follow `.gitignore`; a future reviewed asset exception must be narrow and documented rather than bypassed with a force-add.

Each future feature must state inputs, outputs, owner, failure behavior and meaningful acceptance evidence. Run `python3 -B scripts/check_repository.py` and `python3 -B -m unittest discover -s tests/ci -p 'test_*.py' -v` locally. These run as **Repository checks** in Signova CI for branch pushes and PRs into main. See the [CI runbook](docs/runbooks/continuous-integration.md) for smoke tests and required-check setup. Do not claim a passing empty application suite or call lock placeholders reproducible environments.
