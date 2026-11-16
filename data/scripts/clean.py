# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve source-preserving reviewed photo/video cleaning and quarantine.
# Owner: Basil.
# Expected inputs: Registered authorized originals, qualified label/boundary decisions and
#   approved derivative recipe.
# Expected outputs: Future derivatives plus keep/transform/quarantine/exclude log with
#   before/after hashes and lineage.
# Responsibilities: Preserve signing context, record rotation/color/crop/segment/timestamp
#   mappings and route uncertain cases to review.
# Connections: raw, interim, processed, manifests, configs and Basil audit reports.
# Future implementation: Implement deterministic transformations only from accepted owner
#   input/annotation rules.
# Rules and limitations: Do not overwrite originals, routine-flip, invent neutral, remove
#   linguistic context or silently reassign labels/splits.
# Expected tests or acceptance: Derivatives trace to parent/recipe/reviewer; no lost rows;
#   truncated/ambiguous/rights-unknown assets stay quarantined.
