# .github

Owner: **Hisham**.

Pull-request template and implemented repository CI, owned by Hisham.

| Boundary | Responsibility |
|---|---|
| Receives | Branch pushes, PRs targeting main, optional merge groups and manual runs. |
| Produces | Repository checks and consistent pull-request review evidence. |
| Consumers and dependencies | All contributors and integrated main branch. |
| Never store here | Invented usernames, secrets, private payloads or automatic deployments. |

## Directory contents

| Entry | Purpose |
|---|---|
| [workflows/](workflows/README.md) | Signova CI workflow, events, check name and future application-test guidance. |
| [PULL_REQUEST_TEMPLATE.md](PULL_REQUEST_TEMPLATE.md) | PR review prompts for purpose, module, interfaces, dependencies, evidence, contract impact and reviewer. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

The later CI implementation task authorizes executable workflow/checker code. Frontend,
backend, models and data application source remain comment-only. See the
[CI runbook](../docs/runbooks/continuous-integration.md) for local checks, GitHub verification
and how to require the check before merging.
