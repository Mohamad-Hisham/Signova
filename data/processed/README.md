# data/processed

Owner: **Basil**.

Ignored approved model-facing media/tensor release payloads.

| Boundary | Responsibility |
|---|---|
| Receives | Cleaned reviewed assets, frozen groups/splits and agreed recipes. |
| Produces | Future immutable usable payloads with external release references. |
| Consumers and dependencies | Osama/Bavly dataset loaders and Basil release validation. |
| Never store here | Any ordinary Git payload commit, user session data, credentials or unapproved redistribution. This is not a runtime store. |

## Directory contents

| Entry | Purpose |
|---|---|
| [.gitkeep](.gitkeep) | Empty marker retained alongside the payload-area README; stores no data. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
