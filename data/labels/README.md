# data/labels

Owner: **Basil**.

Stable semantic-label and review/version rules.

| Boundary | Responsibility |
|---|---|
| Receives | Qualified reviewed meanings, sign variety and owner-compatible scope. |
| Produces | Future safe reviewed catalogue distinct from model-specific index order. |
| Consumers and dependencies | Both model owners, Ali public catalogue and Adham Sign Library. |
| Never store here | Guess labels, internal identity metadata or silently reordered model classes. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Semantic versus model mapping

Basil maintains reviewed stable IDs, approved Arabic text, variety/task/status and separate aliases. Osama/Bavly own model-version-specific ordered class indices; Ali publishes only the compatible public subset. Approved English and its public delivery still require Q02/Q10 decisions. Never treat alphabetical folder order as logits order, automatically expose neutral/unknown classes or reuse an ID for a new meaning.
