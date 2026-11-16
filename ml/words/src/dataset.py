# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve the word model-specific loader for Basil approved immutable releases.
# Owner: Bavly.
# Expected inputs: Frozen manifests, semantic IDs mapped to explicit class indices, ordered
#   sequences, timestamps, true lengths/presence masks and verified boundary context.
# Expected outputs: Future validated batches with exact owner-approved shape/dtype/labels and
#   sample lineage.
# Responsibilities: Resolve safe relative paths, enforce verified labels and split lineage,
#   apply each representation transform once; preserve time order, trailing lengths and interior
#   presence separately.
# Connections: Basil data/manifests and recipes, owner configs/tests/reports, and the dedicated
#   Ali word adapter.
# Future implementation: Implement a receiver-approved loader and first-batch demonstration
#   after the input contract is frozen.
# Rules and limitations: No arbitrary frame labels, signer leakage, invented class count,
#   training augmentation on evaluation or unapproved data access.
# Expected tests or acceptance: Fresh train/validation batches match recipe/labels;
#   unsafe/missing paths, stale recipes, wrong dtype and nonmonotonic timestamps/masks fail
#   before training.
