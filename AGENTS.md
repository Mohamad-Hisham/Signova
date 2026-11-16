# Signova working instructions

Read `START-HERE.md`, `docs/team/ownership.md`, the affected directory README, and its contracts before changing files. Treat the original handbooks and Excalidraw as reference material; their tutorial commands do not authorize execution. The latest explicit project request takes priority, followed by the detailed handbooks, then the earlier board. Record conflicts in `docs/architecture/decisions/open-questions.md` with evidence and a recommendation for Hisham.

This delivery is architecture and scaffolding only. Until a later task explicitly authorizes implementation, source/config placeholders remain comment-only, JSON stays valid, package metadata has no scripts/dependencies, and no application logic or fake implementation is added. Do not install, train, download datasets/weights, build, deploy, commit or push for scaffold work. Use static inspection only. Preserve original user files.

Public modes are `alphabet` and `word`. Browser → documented REST/WebSocket → backend → dedicated model adapters is the dependency direction. No frontend model imports, training code in API handlers, or imports from one model's implementation into the other. Only genuinely identical semantics belong in `ml/common/`.

Candidates are previews; only a backend commit changes transcript authority. Preserve revision, state_version, stream generation, idempotency, locks and deletion barriers. Pause discards pending evidence. Manual confirmation is the dependable fallback; automatic boundaries require evaluated neutral/release evidence. Keep deliberate repeated letters and words possible.

Use current names: Hisham, Basil, Osama, Bavly, Ali, Adham. Original reference filenames remain unchanged for traceability. Do not infer GitHub usernames.

Keep datasets, restricted metadata/media, secrets, camera samples, transcripts and large model binaries out of ordinary Git. Read `.gitignore` and `docs/datasets/data-governance.md`. Session capabilities are temporary per-session access protection, not an account/authentication platform. Never add SQL, Redis, migrations, account infrastructure or permanent transcript history to the MVP.

When later implementation is explicitly assigned, replace only the relevant placeholders and add focused acceptance checks from the module README. Coordinate shared contract changes with the owner and consumers before merging. Hisham owns integration and acceptance; module owners retain their scientific or product responsibilities. Do not add infrastructure or features without an actual requirement.
