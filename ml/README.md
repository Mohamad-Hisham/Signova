# ml

Owner: **Osama and Bavly; Hisham coordinates boundaries**.

Separate alphabet and word packages plus genuinely shared tooling specifications.

| Boundary | Responsibility |
|---|---|
| Receives | Basil approved data releases and exact owner task requirements. |
| Produces | Future independently evaluated inference releases and scientific evidence. |
| Consumers and dependencies | backend/ dedicated adapters and artifacts/ release descriptions. |
| Never store here | API route handlers, transcript persistence, frontend imports or a combined classifier. |

## Directory contents

| Entry | Purpose |
|---|---|
| [alphabet/](alphabet/README.md) | Arabic alphabet model package source/config/test/report scaffold. |
| [common/](common/README.md) | Documentation-only shared contract, preprocessing and evaluation extension points. |
| [words/](words/README.md) | isolated Arabic word model package source/config/test/report scaffold. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Independent scientific packages

Alphabet and words keep different mappings, shapes, recipes, temporal requirements, requirements files, tests, reports and releases. Neither source tree imports the other. A common adapter is Ali's boundary, not a universal model pipeline. `ml/common/` remains documentation-only until genuinely identical behavior is demonstrated.

These source layouts are package scaffolds, not currently installable packages: Python package/build names and metadata are future owner decisions. Inference will use architecture/preprocessing/decision modules without importing training entrypoints. No weights, model classes, training functions, predictor code or fake releases exist yet. See `../docs/contracts/model-interface.md` and each owner README.
