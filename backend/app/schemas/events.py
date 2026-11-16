# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve all protocol v1 client messages, server envelopes and event data objects.
# Owner: Ali.
# Expected inputs: Untrusted auth/frame/ping objects and validated service notifications.
# Expected outputs: Future exact v1 parsed inputs/serialized envelopes.
# Responsibilities: Validate version/type, event/session identity, finite timing/scores and
#   message-specific data for every documented type.
# Connections: ws/live.py, common.py, recognition/session/transcript services and frontend
#   validators.
# Future implementation: Define strict protocol schemas and listed reason enumerations after
#   owner review.
# Rules and limitations: No binary v1, invented finish_clip/confirm message, token query or
#   unsupported extra fields.
# Expected tests or acceptance: Three client and eleven server types match docs;
#   wrong-version/unknown-field/nonfinite/oversized inputs fail safely.
