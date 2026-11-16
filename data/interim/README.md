# data/interim

Owner: **Basil**.

Ignored quarantine and source-preserving intermediate derivatives.

| Boundary | Responsibility |
|---|---|
| Receives | Approved raw references, cleaning decisions and recipe versions. |
| Produces | Future reviewed intermediate assets with traceable lineage. |
| Consumers and dependencies | Basil cleaning/annotation and processed-release preparation. |
| Never store here | Any ordinary Git payload commit, user session data, credentials or unapproved redistribution. This is not a runtime store. |

## Directory contents

| Entry | Purpose |
|---|---|
| [.gitkeep](.gitkeep) | Empty marker retained alongside the payload-area README; stores no data. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
