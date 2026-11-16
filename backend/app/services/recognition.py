# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve bounded sample admission, model routing and current candidate/segment
#   orchestration.
# Owner: Ali.
# Expected inputs: Validated ordered JPEGs, current session/stream, approved adapter evidence
#   and capture controls.
# Expected outputs: Future frame acknowledgements, current candidate eligibility and authorized
#   commit intentions.
# Responsibilities: Build owner windows, schedule outside locks, recheck stream/session/capture,
#   enforce hold latch and reset all pending evidence on interruption.
# Connections: Session/transcript/command services, word_gate.py, dedicated model adapters and
#   WS writer.
# Future implementation: Implement cancellation-aware bounded inference and per-stream resource
#   ownership.
# Rules and limitations: Pause never flushes classification; no stale result revival, offline
#   backlog, duplicate artificial frames or fake/model training.
# Expected tests or acceptance: Long gap/overflow/out-of-order resets window; held letters/words
#   once, deliberate new segments repeat; timeout retains native capacity slot.
