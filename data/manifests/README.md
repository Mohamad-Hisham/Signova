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

## Planned manifest fields

The planned manifest covers sample and asset IDs, source and rights references, label and signer metadata, session and parent/group IDs, media details, hashes, dimensions, timing, split and pipeline version. Sample identity and derivative identity have separate uniqueness scopes. Follow the [data governance policy](../../docs/datasets/data-governance.md) for grouping, release access and publication. Public-safe release references can be tracked. Full manifests may remain restricted even with pseudonyms.
