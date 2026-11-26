# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve public /api/v1/models and /api/v1/vocabulary REST boundaries.
# Owner: Hisham.
# Expected inputs: Validated release identity, mode readiness, input limits and approved ordered
#   mapping.
# Expected outputs: Future safe model entries and complete supported public labels.
# Responsibilities: Translate stable IDs/Arabic text, exclude unknown/neutral internals and
#   reflect input:null until manifest validates.
# Connections: Loaded model registry/adapters, schemas/rest/common and Basil reviewed
#   vocabulary.
# Future implementation: Implement read-only metadata routes after real manifests/mapping
#   delivery.
# Rules and limitations: No fake-dev release catalogue, weights/paths, re-sorted logit indices
#   or undocumented English field.
# Expected tests or acceptance: Missing/invalid mode 422; unavailable mapping 503; catalogue
#   lists unavailable modes honestly with deterministic vocabulary order.
