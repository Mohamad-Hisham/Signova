# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve canonical Session, Transcript, Item, Candidate and safe Error response
#   shapes.
# Owner: Ali.
# Expected inputs: Shared documented response fields and owner-approved semantics.
# Expected outputs: Future Pydantic v2 response objects with finite values and correct
#   nullability.
# Responsibilities: Separate transcript revision/state_version, preserve Unicode and provenance,
#   forbid sensitive diagnostics.
# Connections: rest.py, events.py, API/WS serializers and services.
# Future implementation: Define exact handbook fields after remaining deadline/score decisions
#   are closed.
# Rules and limitations: No extra English keys, model tensors, tokens in snapshots or private
#   text in errors.
# Expected tests or acceptance: Canonical snapshots validate; nonfinite scores/invalid modes
#   fail; item/candidate distinction and null edited metadata preserved.
