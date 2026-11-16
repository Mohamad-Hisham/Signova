/*
 * Signova scaffold — documentation placeholder; no implementation.
 * Purpose: Own one video-only permission request and its actual media tracks.
 * Owner: Adham.
 * Expected inputs: Explicit Start/Cancel, selected device constraints and resource generation.
 * Expected outputs: Usable owned MediaStream/status or precise permission/device failure.
 * Responsibilities: Request audio:false, guard late permission/play results, stop all tracks
 *   and clear ownership on every stop.
 * Connections: sessionController.ts, recognition workspace video ownership and sampler.
 * Future implementation: Implement permission/resource lifecycle with track-ended and
 *   simplified-constraint retry handling.
 * Rules and limitations: No auto-start effect, MediaRecorder, hidden camera, model extraction
 *   or transmission authorization in this hook.
 * Expected tests or acceptance: Denied/busy/missing/insecure camera guidance; late grant after
 *   Cancel immediately stops; Strict Mode/unmount/navigation release tracks.
 */
