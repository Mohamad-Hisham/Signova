# Shared repository scripts

Owner: **Hisham; relevant module owner reviews future helpers**.

Repository validation shared by local development and GitHub Actions.

| Boundary | Responsibility |
|---|---|
| Receives | Git checkout files and the repository ignore policy. |
| Produces | Deterministic validation results and useful file/line errors. |
| Consumers and dependencies | GitHub Actions, contributors and CI-tooling regression tests. |
| Never store here | Training/preprocessing copies, secrets, live payloads, installers or deployment logic. |

## Directory contents

| Entry | Purpose |
|---|---|
| [check_repository.py](check_repository.py) | Standard-library repository checks without application dependencies. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Helper policy

```sh
python3 -B scripts/check_repository.py
python3 -B -m unittest discover -s tests/ci -p 'test_*.py' -v
```

Run from the repository root with Python 3.11. Tracked files and unignored local additions
are checked without requiring a commit. Stage intended deletions first so Git lists the
intended checkout. Ignored local payloads are skipped; files force-added despite ignore
rules fail the check. Exit code 1 signals a failed check.

Python is compiled in memory without importing/executing it. JSON must be strict; inline
relative Markdown links/images outside code examples must resolve; module guides and key
ignore protections must remain present. Remote URLs, Markdown anchors/reference-style
links, TypeScript, dependencies and application behavior are outside this check's scope.
It is not a complete secret scanner. Errors contain paths/lines rather than private input.

The later CI task authorizes this helper and its regression tests. Data operations stay
in `data/scripts/`, training/export in model packages, and app logic in frontend/backend.
See the [CI runbook](../docs/runbooks/continuous-integration.md) for hosted smoke tests.
