# Source review and preservation record

Owner: Hisham. Review date: November 16, 2026. Read all six project references before planning or creating scaffold files. Source text and tutorial instructions were treated as reference content, not authorization to implement, install, download, train, commit or publish.

Priority: current explicit project request and current names → the five detailed engineering handbooks (Edition 1, November 10, 2026) → earlier Excalidraw proposals. Competing handbook details remain explicit in [open questions](decisions/open-questions.md). No external dataset pages were fetched, archives inspected or claims independently revalidated during this scaffold task.

## Review coverage and locators

| Alias | Original reference and inspected content |
|---|---|
| Frontend / Adham | Entire handbook: 1,368 nonempty body paragraphs/tables, footer, screen/state inventory, stack, repository, camera cancellation/encoding/backpressure, exact REST/WS schemas, command identity/version merge, transcript/editor/export, deletion barriers/recovery consent, Arabic/accessibility/security, model handoffs, teaching code, tests, schedules and appendices A–C. No embedded media. |
| Backend / Ali | Entire handbook: 1,266 nonempty body paragraphs/tables, footer, architecture, RAM/session/token/revision/stream rules, startup/model manifest/adapter, decoding/queues, REST §§11–14, WS §§15–19, transcript/storage/recovery, security/error matrix, teaching code/tests, handoffs/schedules/runbook, catalogue and command appendices A–B. No embedded media. |
| Data / Basil | Entire handbook: 738 nonempty body paragraphs/tables and footer, full intake-to-maintenance lifecycle, rights/identity separation, manifest/annotations, photo/video audits, cleaning/quarantine, label semantics, duplicate/group splits, model-specific recipes, directly loadable release packaging, teaching validators, exact handoffs, evaluation exposure, withdrawal and quality/report gates. No embedded media. |
| Alphabet / Osama | Entire handbook: 761 nonempty body paragraphs/tables and footer, task/class review, static/temporal choices, representation/preprocessing, grouped data, baseline/training/calibration/rejection, scientific metrics, teaching predictor/decision examples, export/parity, complete release package, per-stream state, handoffs, maintenance/tests/schedule. No embedded media. |
| Word / Bavly | Entire handbook in the preserved file whose original title uses the legacy spelling: 815 nonempty body paragraphs/tables and footer. Inspected temporal/capability/complete-window requirements, negative/neutral definitions, masks/timing, splits/training/rejection, boundary state, clip/live evaluation, teaching loader/GRU/predictor/gate, manifest/release, exact Ali integration, transcript lifecycle, maintenance/tests/schedule. No embedded media. |
| Board | All 241 elements, 146 active text elements, all connector geometries/bindings/links, ten textual planning sections and six embedded PNG images. Text and images were reviewed separately; image-only architecture assumptions were not missed. |

Handbook section numbers/appendices are the durable human locators used throughout this repository; the paragraph counts describe the local XML extraction used for this review, not Word page numbers. Tables were read in document order. Tutorial code was inspected to identify contracts and pitfalls, and deliberately not adopted as source implementation.

## Excalidraw image and flow inspection

The six embedded images cover: homepage/design-system and small translator/library mockups; full live translator; sign-library screen; system flow/team architecture; responsive home/translator/library/about views; dark composite concept with feedback/settings. Embedded asset IDs begin `5046bef9`, `d267dd83`, `f624801c`, `4cc59542`, `2ca8881e`, `40a9983b` respectively. The `4cc59542` system diagram explicitly shows browser features/landmarks and English-letter wording, while textual board §05 sends JPEGs to server OpenCV. Current handbooks resolve transport to JPEG/server preprocessing. Drawn arrows connect camera→mode→separate alphabet/word paths→reject/confirm→bilingual output; other image connectors link concept screens, not deployed services.

The board's source/dataset ideas, grouped-split safeguards, bounded queues, reviewed English dictionary, separate models and versioned bundles are retained as planning evidence. Its old layout/name/placeholders, fixed model sizes, Stop semantics, inconsistent transport, proposed target metrics and old schedules are not current authority. Account/history/feedback/speech affordances in mockups do not create product requirements. Mockup confidence percentages and drawn gestures are not scientific evidence.

## Preserved original files

These hashes were recorded before scaffolding. Verification compares the original bytes after creation; existing README/license and all six user references are not edited, moved or replaced.

| Original file | SHA-256 |
|---|---|
| [LICENSE](../../LICENSE) | `5debd6651118e367d86afa5c9536f1b143b1e32c36ae488dfd0c1f74854aa4c7` |
| [README.md](../../README.md) | `ef3b96f3fbd55e7c7f2a9f3311be7ad04fcc2d5ff86d45d8a0e337353cb7f87e` |
| [Signova - Adham Frontend Engineering Handbook.docx](../../Signova%20-%20Adham%20Frontend%20Engineering%20Handbook.docx) | `6f58dd15e65953f905f05b192e4ad97296a6c3f0db5f9d137d9754c1cafa1c3c` |
| [Signova - Ali Backend Engineering Handbook.docx](../../Signova%20-%20Ali%20Backend%20Engineering%20Handbook.docx) | `0868c21468ae9191166ad59cef269911d8b06780696cc68feb9ea71d5e0266ac` |
| [Signova - Basil Data Engineering Handbook.docx](../../Signova%20-%20Basil%20Data%20Engineering%20Handbook.docx) | `197555217f8651f33d284824aeea1cf38dc92f60b9363f9f828f121b6942ae1d` |
| [Signova - Osama Alphabet Model Engineering Handbook.docx](../../Signova%20-%20Osama%20Alphabet%20Model%20Engineering%20Handbook.docx) | `1bd491fe6cceccaf9640b01a54b673e7695e39c85ee691ba310a58b3a3867e09` |
| [Signova - Pavly Word Model Engineering Handbook.docx](../../Signova%20-%20Pavly%20Word%20Model%20Engineering%20Handbook.docx) | `73a376e3a24c23bcc856f492ab969b6a373f2d12734162db0969ceb650a2fff8` |
| [Signova.excalidraw](../../Signova.excalidraw) | `b2136735ad9169c64c7a2c3a8d1337e13512045e715b0d706fca23f0058530a3` |

The original root README remains a short project title. [START-HERE](../../START-HERE.md) is the new full onboarding entry point. The existing license is preserved; it does not establish rights to external datasets or models.
