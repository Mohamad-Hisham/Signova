/*
 * Signova scaffold — documentation placeholder; no implementation.
 * Purpose: Display only current candidate evidence and Confirm eligibility.
 * Owner: Adham.
 * Expected inputs: Validated candidate/null, active stream/status, expiry and pending-command
 *   state.
 * Expected outputs: Arabic preview, optional approved English equivalent and explicit Confirm
 *   intent.
 * Responsibilities: Clear stale previews, disable expired/consumed/pending candidates and
 *   explain stable/waiting/unknown states.
 * Connections: Recognition workspace, controller and future approved vocabulary mapping.
 * Future implementation: Implement visual candidate presentation and candidate-specific expiry
 *   feedback.
 * Rules and limitations: Do not append text, generate item IDs, compute backend stability or
 *   call a score percent accuracy; English delivery is unresolved.
 * Expected tests or acceptance: Old-stream/null/stale candidate cannot confirm; confirmation
 *   pending disables repeat action without erasing confirmed transcript.
 */
