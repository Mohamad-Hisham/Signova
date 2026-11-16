# Architecture decisions

Owner: Hisham; evidence and review supplied by affected module owners. Receives the latest explicit project instructions, handbook conflicts, integration findings and evaluated model/data releases. Produces accepted decisions, pending questions and coordinated contract updates consumed by all modules. Never store private user payloads, tokens, restricted source evidence or invented performance claims here.

[Open questions](open-questions.md) distinguishes decisions still needed from older proposals already superseded by the current request. Recommendations are proposals until Hisham and the named technical owners accept them; a scaffold placeholder is not implementation evidence.

Accepted baseline from the current request: one modular monorepo, React/TypeScript/Vite, one FastAPI backend with Python 3.11 as an initial target, separate alphabet and word packages, JPEG-to-server v1 transport, backend RAM transcript authority, manual confirmation fallback, no permanent history/database/Redis/accounts, and Pause discarding all pending recognition. Public mode names remain `alphabet` and `word`. Keep one backend process/worker/replica.

Record a future decision with ID/date, concrete question, source sections, competing options, chosen outcome, rationale, owners/consumers, evidence, contract/version consequences and remaining limitations. Update this log and affected contracts together; use a separate ADR file only when its detail warrants one. Do not silently change an API field, model representation, label meaning or data split to resolve a mismatch.
