# data/features

Owner: **Basil**.

Ignored owner-specific extracted tensors/features with timing and masks.

| Boundary | Responsibility |
|---|---|
| Receives | Approved data release and exact versioned feature recipe. |
| Produces | Future reproducible caches linked to parents/split/extractor version. |
| Consumers and dependencies | Model-owner loaders and Ali permitted parity reference checks. |
| Never store here | Any ordinary Git payload commit, user session data, credentials or unapproved redistribution. This is not a runtime store. |

## Directory contents

| Entry | Purpose |
|---|---|
| [.gitkeep](.gitkeep) | Empty marker retained alongside the payload-area README; stores no data. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
