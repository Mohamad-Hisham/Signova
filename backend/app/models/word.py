# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve the dedicated Bavly temporal word runtime adapter.
# Owner: Ali.
# Expected inputs: Trusted word package, owner-approved ordered samples/times/features and
#   per-stream context.
# Expected outputs: Future shared usable/rejected/neutral evidence and documented
#   reset/readiness outcomes.
# Responsibilities: Honor exact sampling/window/masks/feature recipe, capability flags, class
#   order and per-stream extractor/recurrent state.
# Connections: base.py, ml/words/src/predict.py and preprocessing.py, recognition/word gate and
#   artifact metadata.
# Future implementation: Choose and wrap the agreed frame-versus-feature callable boundary with
#   Bavly.
# Rules and limitations: No alphabet imports, universal sequence length, generated neutral from
#   low score or clip-only model advertised live-compatible.
# Expected tests or acceptance: Golden tensor/decision parity, insufficient
#   sequence/gaps/reset/concurrent streams and timeout behave safely; no cross-user hidden
#   state.
