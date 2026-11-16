# Signova scaffold — documentation placeholder; no implementation.
# Purpose: Reserve safe uniform REST/WS failure construction and redaction conventions.
# Owner: Ali.
# Expected inputs: Reviewed error code, retryability, field paths/current revision and safe
#   request context.
# Expected outputs: Future documented error envelope and protocol-appropriate status/close
#   guidance.
# Responsibilities: Map known validation/state/runtime failures without echoing private input or
#   framework traces.
# Connections: REST/WS layers, strict schemas and all services.
# Future implementation: Implement content-free error mapping and safe support/request IDs.
# Rules and limitations: No tokens, rejected image/text values, transcript snapshots, filesystem
#   paths or stack traces in responses/logs.
# Expected tests or acceptance: 422 safe path/reason, 409 revision without text, generic
#   wrong-token 404 and safe internal errors match contracts.
