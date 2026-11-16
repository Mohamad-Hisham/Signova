# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve the exact deterministic word training-evaluation-serving input recipe.
# Owner: Bavly.
# Expected inputs: Validated oriented RGB samples or owner-approved features plus
#   timestamps/quality/presence information.
# Expected outputs: Future tensor/features of documented names, dtype, axes, range and numerical
#   tolerances.
# Responsibilities: Make color/orientation/crop/pad/resize/scaling/extractor behavior explicit;
#   preserve temporal order, interior missing steps and distinct trailing padding/length
#   semantics.
# Connections: Basil offline recipe, dataset.py, predict.py, configs and Ali dedicated adapter
#   parity checks.
# Future implementation: Implement owner-local recipe first; extract genuinely identical
#   utilities to ml/common only with both model owners review.
# Rules and limitations: No guessed dimensions, double normalization, routine mirroring,
#   test-fitted parameters or feature-version substitution.
# Expected tests or acceptance: Same permitted fixture matches offline/runtime intermediates
#   within declared tolerance; portrait/context/gap/missing evidence cases explicit.
