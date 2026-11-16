# GitHub Actions workflows

Owner: **Hisham; affected module owners review future application test jobs**.

Implemented repository checks; application modules remain scaffolds.

| Boundary | Responsibility |
|---|---|
| Receives | Branch pushes, PRs into main, optional main merge groups and manual dispatch. |
| Produces | The Repository checks job in the Signova CI workflow. |
| Consumers and dependencies | Contributors, PR reviewers and main branch protection. |
| Never store here | Secrets, user data, model binaries, dataset downloads or deployment credentials. |

## Directory contents

| Entry | Purpose |
|---|---|
| [ci.yml](ci.yml) | Runs checker regression tests and repository validation with Python 3.11. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Events and scope

`push` covers all branches, including main after merging. `pull_request` targets main and
keeps checkout's default merge revision. `merge_group` supports a future merge queue.
`workflow_dispatch` allows manual runs once this file reaches the default branch. Branch
push and PR runs are separate; older runs for the same event/ref can be cancelled when
a newer update arrives. There are no path filters that could skip a required check.

The job uses read-only access, does not persist checkout credentials, and pins official
checkout/setup-python actions to full hashes with release comments. No project dependencies
are installed. Review action pin updates against their official releases.

Current checks validate Python syntax without executing application modules, strict JSON,
inline relative Markdown links, module guides, key ignore protections and tracked files
that violate `.gitignore`. Checker regression tests run first. Frontend builds, Pytest,
TypeScript checks, browser tests and model evaluation require real implementation, tested
locks and meaningful suites. No empty application suite is reported as passing.

See the [CI runbook](../../docs/runbooks/continuous-integration.md) for exact commands,
GitHub success/failure tests and required-check setup.
