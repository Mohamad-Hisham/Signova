# data/scripts

Owner: **Basil**.

Offline inventory, cleaning, splitting, release validation and packaging placeholders.

| Boundary | Responsibility |
|---|---|
| Receives | Explicitly authorized assets and documented deterministic rules. |
| Produces | Future reproducible derivative/audit/release actions, never live-session processing. |
| Consumers and dependencies | Basil data workflow and model receiver acceptance. |
| Never store here | Executed scripts in this scaffold, silent source deletion, live collection or data downloads. |

## Directory contents

| Entry | Purpose |
|---|---|
| [build_manifests.py](build_manifests.py) | Reserve stable sample/asset/annotation and safe release manifest assembly. |
| [clean.py](clean.py) | Reserve source-preserving reviewed photo/video cleaning and quarantine. |
| [inventory.py](inventory.py) | Reserve source intake and photo/video inventory without altering originals. |
| [package_release.py](package_release.py) | Reserve immutable directly usable alphabet/word data-release packaging and lineage references. |
| [split.py](split.py) | Reserve deterministic signer/session/parent/duplicate-aware split assignment. |
| [validate_release.py](validate_release.py) | Reserve hard dataset release checks and receiver compatibility validation. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |
