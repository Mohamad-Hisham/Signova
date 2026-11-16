# ml/common/evaluation

Owner: **Osama and Bavly jointly**.

Reserved common metric/report convention documentation.

| Boundary | Responsibility |
|---|---|
| Receives | Explicit populations, label orders and independent-group protocols. |
| Produces | Future reusable metric/report helpers with declared denominators. |
| Consumers and dependencies | Owner-local evaluations and Basil audit. |
| Never store here | Shared thresholds/performance claims that erase task-specific recognition/event differences. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Metric conventions

Any later shared helper must state supported/negative populations, accepted-only accuracy with coverage, undefined-denominator behavior, fixed class order and independent grouping. Word live-event matching/completion/duplicates and alphabet per-letter/static/temporal coverage remain distinct. Unit correctness never proves recognition accuracy. No metric implementation or results are provided.
