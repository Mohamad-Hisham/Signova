/*
 * Signova scaffold — documentation placeholder; no implementation.
 * Purpose: Mirror approved public REST/WS types and selected Zod runtime validation.
 * Owner: Adham.
 * Expected inputs: Untrusted network JSON and central docs/contracts specifications.
 * Expected outputs: Validated public session/transcript/item/candidate/event objects or safe
 *   schema failures.
 * Responsibilities: Validate mode word/alphabet, finite scores, IDs/versions, timestamps and
 *   all message-specific required fields.
 * Connections: REST client, liveSocket, reducer and contract acceptance fixtures.
 * Future implementation: Define types/runtime schemas after shared decisions without encoding
 *   tutorial-only shortcuts.
 * Rules and limitations: No model tensor types, new English wire field, unannounced keys or
 *   TypeScript casts replacing validation.
 * Expected tests or acceptance: Missing/unknown/wrong-version/session fields fail safely; valid
 *   canonical snapshots preserve Unicode and nullable provenance.
 */
