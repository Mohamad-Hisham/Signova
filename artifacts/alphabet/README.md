# artifacts/alphabet

Owner: **Osama; Ali verifies runtime acceptance**.

Model-specific release handoff specification and future safe approved references.

| Boundary | Responsibility |
|---|---|
| Receives | Complete immutable owner package, checksums, evidence and permissions. |
| Produces | Future externally stored version references tied to model/data/recipe versions. |
| Consumers and dependencies | Ali dedicated adapter/startup and Hisham release acceptance. |
| Never store here | Weights/checkpoints, fabricated releases, private golden media or in-place replacement of published bytes. |

## Directory contents

| Entry | Purpose |
|---|---|
| [RELEASE-TEMPLATE.md](RELEASE-TEMPLATE.md) | Model-specific complete release checklist and future immutable external reference format without fake artifacts. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
