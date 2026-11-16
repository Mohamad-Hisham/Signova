# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve Ali common adapter evidence and runtime lifecycle interface.
# Owner: Ali.
# Expected inputs: Owner-specific approved predictor outputs and validated model-bound samples.
# Expected outputs: Future normalized evidence plus model version/readiness/reset semantics.
# Responsibilities: Hide runtime/tensor/class-index differences from networking and explicitly
#   distinguish usable, rejected and evaluated neutral.
# Connections: alphabet.py, word.py, fake.py, model-interface contract and recognition service.
# Future implementation: Declare common interface only after rejected-score and callable-layer
#   decisions are accepted.
# Rules and limitations: No shared hardcoded tensor shape, false neutral, browser schema leakage
#   or enforced identical model preprocessing.
# Expected tests or acceptance: Both adapters map trusted IDs/finite scores and reject invalid
#   output; null raw-score handling follows recorded decision.
