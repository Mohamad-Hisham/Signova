# Local development: scaffold status and future setup

Owner: Hisham coordinates; Adham owns frontend setup, Ali backend integration, Basil offline data tools, Osama/Bavly separate model environments. Inputs: an explicitly assigned implementation issue and approved contracts/releases. Output: a later reproducible development environment. No working application or tested dependency lock exists in this delivery.

For this scaffold, inspect [START-HERE](../../START-HERE.md), source placeholders, READMEs, [contracts](../contracts/README.md), [open questions](../architecture/decisions/open-questions.md) and [verification](scaffold-verification.md). Do not install dependencies, run Vite/Uvicorn, invoke package managers, train, download datasets/weights, build, deploy or run application tests. Comment-only requirements files are not install manifests/locks; `package.json` has no scripts/dependencies, `tsconfig.json` is an empty valid object, HTML has no executable entrypoint, and Python modules expose no app.

## Future owner-led implementation setup

Repository CI tooling is implemented separately from the application scaffold. Run
`python3 -B scripts/check_repository.py` and
`python3 -B -m unittest discover -s tests/ci -p 'test_*.py' -v` without installing packages.
See [continuous integration](continuous-integration.md) for hosted verification. The
application startup/build/test restrictions above still describe the unimplemented app.

After separate implementation authorization, Ali/model owners verify Python 3.11 compatibility against both actual inference runtimes in one backend process. Adham selects a maintained Node LTS compatible with the chosen Vite/test versions at implementation time. Each owner records tested dependencies and recreates its lock in a clean environment; training environments can remain independent. Do not claim compatibility from a successful install alone or run empty lockfiles as if reproducible.

Frontend stack: React, TypeScript, Vite, native Fetch/WebSocket, Zod, Vitest, React Testing Library and Playwright. Backend stack: Python 3.11 initial target, FastAPI, Pydantic v2, Uvicorn, NumPy, Pillow, Pytest, HTTPX and Ruff; typed settings tooling and model runtime depend on tested requirements. OpenCV/MediaPipe are conditional model-recipe dependencies, not browser defaults. Model architectures/runtimes remain evidence-dependent.

Frontend's future public settings are `VITE_API_BASE_URL=http://localhost:8000/api/v1` and `VITE_WS_BASE_URL=ws://localhost:8000/api/v1`; they appear as comments only in `.env.example` now. Vite settings are public, never session/model secrets. Ali must choose actual server setting names for exact origins, trusted artifact paths, RAM/time/rate limits and confirmation policy. Keep local `.env` files ignored. Agree the exact frontend origin and both base paths before connecting camera traffic.

A future first integration slice uses an explicitly labeled deterministic development adapter and synthetic fixtures. `fake.py` currently contains comments only. It must never silently replace missing real models in release readiness or demonstrations. Implement camera cleanup, revisions, idempotency, cancellation and transcript actions before relying on real model accuracy.

Use one backend process/worker/replica. Reload/restart destroys sessions; no database or Redis is available to restore them. Model startup requires approved artifact checksums, runtime verification, warmup/golden tests and per-mode readiness. Dataset access and model artifacts use separately approved external locations; never add download-on-request behavior.

When implementation exists, publish actual run/build/test commands in module READMEs and this runbook from the tested environment. Do not copy handbook starter commands blindly into CI. Focus acceptance on a complete user journey and meaningful failures, with hardware/browser/versions recorded.
