# .github/workflows

Owner: **Hisham with Adham/Ali/model-owner input**.

README describing future CI responsibilities; no YAML workflow.

| Boundary | Responsibility |
|---|---|
| Receives | Actual later package scripts, tested locks and safe acceptance suites. |
| Produces | Future lint/type/unit/contract checks only when their implementation exists. |
| Consumers and dependencies | Pull requests and maintainers. |
| Never store here | Runnable workflows, meaningless empty test gates, model/data downloads or deployment credentials. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Future CI, currently inactive

Only this README exists here. Add workflow YAML later when real frontend scripts, tested Python locks and meaningful suites exist. Possible checks include formatting/lint/type checking, focused unit/contract tests and synthetic integration; heavy scientific evaluation belongs in a reviewed model process. Never report empty suites as acceptance or download restricted data/weights automatically in public CI. No deploy/publish workflow is part of this task.
