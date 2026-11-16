/*
 * Signova scaffold — documentation placeholder; no implementation.
 * Purpose: Own explicit browser clipboard and local/authorized-server TXT download
 *   interactions.
 * Owner: Adham.
 * Expected inputs: Chosen confirmed/local-copy text and revision, explicit gesture and optional
 *   export response.
 * Expected outputs: Clipboard success/failure or requested user-controlled UTF-8 text download.
 * Responsibilities: Distinguish draft/confirmed copy, handle permission failure and 204/409
 *   exports, revoke object URLs.
 * Connections: TranscriptPanel, controller and REST client for authorized export.
 * Future implementation: Implement native clipboard/Blob actions with selectable-text fallback.
 * Rules and limitations: No external conversion service, server history, automatic download or
 *   claim that a requested file was safely saved.
 * Expected tests or acceptance: Denied copy is honest; Arabic punctuation/digits open
 *   correctly; offline local download works; export never changes revision.
 */
