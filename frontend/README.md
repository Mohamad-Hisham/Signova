# frontend

Owner: **Adham**.

One React/TypeScript/Vite application scaffold and browser acceptance descriptions.

| Boundary | Responsibility |
|---|---|
| Receives | Ali REST/WebSocket contracts, public-safe vocabulary and owner-approved camera requirements. |
| Produces | Future JPEG samples/actions, preview/editor/display state and explicit local copy/download. |
| Consumers and dependencies | Users, backend/ contract integration and shared tests/. |
| Never store here | Python/model imports, weights, training code, session secrets in VITE settings or default camera recordings. |

## Directory contents

| Entry | Purpose |
|---|---|
| [e2e/](e2e/README.md) | Future Playwright full-browser acceptance scenarios. |
| [src/](src/README.md) | Comment-only application, network, camera, features, shared UI, style and mock planning files. |
| [tests/](tests/README.md) | Future Vitest/React Testing Library acceptance specifications. |
| [.env.example](.env.example) | Describe future public API/WS base URL settings without assigning or storing secrets. |
| [index.html](index.html) | Reserve the future accessible HTML document and single browser mount point. |
| [package.json](package.json) | Minimal valid project identity only; no dependencies, scripts, runnable entrypoint or lock claims. |
| [tsconfig.json](tsconfig.json) | Valid empty JSON placeholder; future compiler/JSX/strictness options are documented in frontend README. |
| [vite.config.ts](vite.config.ts) | Reserve future Vite development/build and test-compatible configuration. |
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Current files and future configuration

`package.json` is minimal valid project metadata (`name`, `version`, `private`); it has no scripts or dependencies. `tsconfig.json` is a valid empty object, not an active compiler setup. `vite.config.ts`, `index.html` and every TS/TSX/CSS file contain comments only. No frontend can start or build yet, and no package lock is fabricated.

During separately assigned implementation, Adham will select compatible React/TypeScript/Vite versions; configure strict compiler checking, JSX/module/browser targets and Vite types; add only required packages and real scripts; then generate/recreate the tested dependency lock. Native Fetch/WebSocket, Zod, Vitest, React Testing Library and Playwright are the chosen stack. No Axios, Socket.IO, model runtime or account/history platform is needed by the current contract.

Public API/WS URL names are documented as comments in `.env.example`; they are never secret storage. `main.tsx` will own mounting, App composition, the reducer serializable state, and the controller all media/network side effects. Feature views receive state/callbacks. Test locations are `tests/` and `e2e/`; no runnable tests exist now. Read `../docs/contracts/frontend-backend-contract.md` before implementing a screen.
