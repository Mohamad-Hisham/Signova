# Git workflow

Owner: Hisham. One repository, one integrated `main`, one accountable owner per issue. There are no separate model/frontend/backend repositories and no generated GitHub identities.

1. Open an issue naming module, owner, input/output contract, dependencies, acceptance criteria and relevant decision IDs. Restricted evidence is referenced safely rather than pasted.
2. Create a short feature branch from current `main`; examples: `feature/words-input-contract`, `feature/frontend-editor`, `docs/data-release`. Keep one coherent change per branch.
3. Make small, understandable changes in the owned module; coordinate affected owners before changing shared routes, fields, labels, preprocessing, split rules or model semantics.
4. Open a pull request using `.github/PULL_REQUEST_TEMPLATE.md`; explain resulting behavior, interface impact, dependencies and reproducible evidence.
5. Obtain peer review from a teammate able to assess the changed module. Shared-boundary changes need the owner and consuming side; Hisham coordinates disputes and integration risk.
6. Run the repository checker and CI-tooling tests, then verify **Repository checks** passes on the PR. GitHub checks the combined PR/main revision and checks main again after a merge. Add actual application suites as implementation arrives; no empty-suite success claim. See the [CI runbook](../runbooks/continuous-integration.md) for commands and branch-protection setup.
7. Merge approved changes into `main` and close the issue with its evidence. Keep main as the integrated project foundation, and reproducible/runnable once implementation exists.

The original scaffold task did not create active CI. The later authorized CI task adds the checker/tests and workflow; GitHub runs start once contributors push it. No commit, push, PR, merge or repository settings change is performed by the CI authoring task. Preserve user work and review the diff before committing. Do not force-add ignored recordings, restricted manifests, secrets or weights. Approved tiny public assets require a narrow reviewed ignore exception and provenance, never broad unignoring of datasets.

A contract-changing PR updates the central contract, success/failure examples, version/migration implications, producer/consumer placeholders or implementation as applicable, and acceptance checklist together. No teammate silently adjusts another owner's expected input or invents fields to unblock themselves.
