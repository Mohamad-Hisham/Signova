# tests/contracts

Owner: **Hisham coordinates Ali/Adham and model/data owners**.

Future producer/consumer schema and version consistency scenarios.

| Boundary | Responsibility |
|---|---|
| Receives | Exact REST/WS/model/data/vocabulary contract revisions. |
| Produces | Future evidence that both sides accept the same inputs/outputs/errors. |
| Consumers and dependencies | Frontend/backend and model/data integration reviews. |
| Never store here | Duplicated alternative schema authority, network secrets or unreviewed fixture payloads. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Future producer/consumer consistency

Cross-check Python response/TypeScript runtime schema shapes, every REST status/WS reason, mode word versus directory words, model evidence/nullability, dataset lineage/units and vocabulary version/class order. Include negative/unknown-key/wrong-version examples. Contract files remain the authority; this directory must not become an unreviewed alternative schema definition. No executable tests exist now.
