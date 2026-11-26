# backend/tests/fixtures

Owner: **Hisham with Basil permission review**.

Safe future synthetic request/event descriptions and approved tiny golden references.

| Boundary | Responsibility |
|---|---|
| Receives | Exact schemas and versioned owner expectations with rights records. |
| Produces | Future reproducible accepted/rejected cases for backend tests. |
| Consumers and dependencies | Backend unit/integration tests and shared fixtures review. |
| Never store here | Actual user payloads, live tokens, unapproved media or fake placeholder bytes presented as images. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Fixture boundary

Plan schema-valid synthetic requests, snapshots, events and fake-clock traces; later decoding needs actual valid tiny JPEG bytes and model parity needs permitted owner fixtures with numerical tolerances. Placeholder text is not an image. File bytes use exact hashes; floating intermediates use approved tolerances. Binary media is ignored by default and needs a narrow reviewed exception or controlled external reference.
