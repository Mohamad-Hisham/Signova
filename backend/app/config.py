# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve typed runtime settings and validated startup policy.
# Owner: Ali.
# Expected inputs: Later environment/origin/artifact/timeout/capacity settings and
#   owner-approved manifests.
# Expected outputs: Future validated immutable configuration or safe startup failure.
# Responsibilities: Validate exact origins, trusted model paths, per-mode requirements, bounded
#   queues/deadlines and manual/automatic policy.
# Connections: main.py, session/recognition services, adapters and public safe catalogue.
# Future implementation: Define Pydantic v2-compatible typed settings after field names and
#   runtime requirements are approved.
# Rules and limitations: No credentials committed, browser-selected model paths, guessed tensor
#   sizes or multiple replicas with RAM sessions.
# Expected tests or acceptance: Incompatible required fps/window rejected; secrets/paths absent
#   from public errors; initial values labeled as starting settings.
