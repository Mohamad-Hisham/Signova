# data/manifests

Owner: **Basil**.

Safe manifest/split/lineage schema documentation and future reviewed release references.

| Boundary | Responsibility |
|---|---|
| Receives | Stable sample/asset/parent/group IDs and frozen split decisions. |
| Produces | Future public-safe metadata only; full restricted manifests remain controlled. |
| Consumers and dependencies | Model loaders, validation/release tools and Basil lineage audit. |
| Never store here | Local absolute paths, identifying raw filenames, private group registries or invented rows. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Schema authority

`../../docs/contracts/dataset-contract.md` defines future sample/asset/source/rights/label/signer/session/parent/group, media/hash/dimension/time, split and pipeline fields. Public-safe release references can be tracked; full manifests may remain restricted even with pseudonyms. Sample identity and derivative identity have separate uniqueness scopes. No invented CSV/JSONL rows are provided.
