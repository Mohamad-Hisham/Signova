# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve strict REST creation, capture, confirm, space, replacement, clear and end
#   input schemas.
# Owner: Ali.
# Expected inputs: Untrusted documented request bodies/query/header identities.
# Expected outputs: Future validated operation inputs or safe field-path validation errors.
# Responsibilities: Forbid unknown fields, enforce nonboolean integers, UUID command headers,
#   text/code-point and body limits.
# Connections: api handlers, common.py and commands/transcript services.
# Future implementation: Define Pydantic v2 request contracts with exact v1 field names.
# Rules and limitations: Do not accept client score/source/label provenance, guessed revisions,
#   mode changes or empty bodies on no-body routes.
# Expected tests or acceptance: Missing/extra fields, duplicate/foreign IDs and malformed
#   revisions return safe 422 before mutation; valid stale revisions use 409.
