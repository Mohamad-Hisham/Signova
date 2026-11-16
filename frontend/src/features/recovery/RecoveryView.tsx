/*
 * Signova scaffold — documentation placeholder; no implementation.
 * Purpose: Explain reconnection, expiry and recovered local copy without claiming active server
 *   state.
 * Owner: Adham.
 * Expected inputs: Validated optional cached snapshot and actual authorized GET/socket outcome.
 * Expected outputs: Explicit Copy/Download/Remove-local-copy or fresh-session intentions.
 * Responsibilities: Keep camera off, label a missing/restarted backend copy honestly and stop
 *   terminal reconnect loops.
 * Connections: Controller, recoveryStore and transcriptActions.ts.
 * Future implementation: Implement recovering/offline/expired/local-copy states with deliberate
 *   navigation.
 * Rules and limitations: No silent upload, new session recreation, old candidate replay or
 *   claim that local text is cloud history.
 * Expected tests or acceptance: Refresh off loses memory; refresh on prefers live snapshot;
 *   restart yields labeled local copy and no automatic capture.
 */
