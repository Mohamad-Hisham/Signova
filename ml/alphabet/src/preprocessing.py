# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve the exact deterministic alphabet training-evaluation-serving input recipe.
# Owner: Osama.
# Expected inputs: Validated oriented RGB samples or owner-approved features plus approved
#   single-image or sequence context.
# Expected outputs: Future tensor/features of documented names, dtype, axes, range and numerical
#   tolerances.
# Responsibilities: Make color/orientation/crop/pad/resize/scaling/extractor behavior explicit;
#   preserve full required hand/body context and approved handedness distinctions.
# Connections: Basil offline recipe, dataset.py, predict.py, configs and Ali dedicated adapter
#   parity checks.
# Future implementation: Implement owner-local recipe first; extract genuinely identical
#   utilities to ml/common only with both model owners review.
# Rules and limitations: No guessed dimensions, double normalization, routine mirroring,
#   test-fitted parameters or feature-version substitution.
# Expected tests or acceptance: Same permitted fixture matches offline/runtime intermediates
#   within declared tolerance; portrait/context/gap/missing evidence cases explicit.
