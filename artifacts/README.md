# artifacts

Owner: **Hisham and Ali coordinate; model owners own scientific releases**.

Safe model-release descriptions, model-specific templates and future immutable external pointers.

| Boundary | Responsibility |
|---|---|
| Receives | Model manifests/evidence and approved binary storage references. |
| Produces | Future traceable release metadata consumed at backend startup. |
| Consumers and dependencies | Ali model registry/readiness and QA/reproducibility review. |
| Never store here | Fake weights/manifests, actual large binaries, restricted media or browser-uploaded arbitrary models. |

## Directory contents

| Entry | Purpose |
|---|---|
| [alphabet/](alphabet/README.md) | Model-specific release handoff specification and future safe approved references. |
| [words/](words/README.md) | Model-specific release handoff specification and future safe approved references. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## External release boundary

This directory contains only model-release policy/templates and future safe references, not a storage backend or real release. No fake weight, manifest.json, labels.json, checksum value or approved model version is supplied. Each future reference ties actual immutable model/data/split/labels/recipe/policy versions and hashes to an external approved package.

Do not require identical filenames across model owners; declare real paths in each manifest. Ali verifies checksums/runtimes, loads once and runs warmup/golden checks before marking a mode ready. Large binaries and restricted fixtures remain outside ordinary Git. See the [model interface and release contract](../docs/contracts/model-interface.md).
