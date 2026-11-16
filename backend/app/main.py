# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve the one FastAPI application composition and lifecycle boundary.
# Owner: Ali.
# Expected inputs: Reviewed server settings and both trusted approved inference packages.
# Expected outputs: Future application lifecycle and per-mode readiness; no app object exists
#   yet.
# Responsibilities: Verify artifacts/runtimes, load once, warmup/golden check, attach
#   routes/socket/services and start bounded cleanup ownership.
# Connections: config.py, api/, ws/live.py, model adapters and sessions service.
# Future implementation: Implement startup/shutdown composition only after runtime and
#   implementation authorization.
# Rules and limitations: One process/worker/replica; no model download/import-time training,
#   request-local loads or fake readiness fallback.
# Expected tests or acceptance: Missing/corrupt artifact leaves mode unready; lifespan loads
#   once; shutdown drops session/model resources without disk dumps.
