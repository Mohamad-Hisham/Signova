# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve separate monotonic deadline/stability timing and UTC display timestamps.
# Owner: Ali.
# Expected inputs: Future injected clock source and accepted session/candidate events.
# Expected outputs: Future deterministic elapsed/deadline calculations and UTC ISO timestamps.
# Responsibilities: Keep browser capture time, server monotonic intervals and public wall-clock
#   timestamps distinct.
# Connections: Session expiry, commands, recognition/word gate and deterministic tests.
# Future implementation: Implement clock abstraction suitable for fast fake-clock acceptance
#   without sleeping.
# Rules and limitations: Do not infer cross-machine latency from browser timestamps or use
#   wall-clock jumps to control gates.
# Expected tests or acceptance: Idle/absolute/grace and candidate expiry deterministic;
#   clock-skew display honest; heartbeat never extends idle.
