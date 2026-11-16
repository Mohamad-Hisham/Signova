# backend/tests/unit

Owner: **Ali**.

Future isolated command/session/transcript/gate/validation acceptance.

| Boundary | Responsibility |
|---|---|
| Receives | Fake clock and synthetic state/evidence traces. |
| Produces | Future revision, expiry, latch and text-invariant evidence. |
| Consumers and dependencies | Backend services and Hisham integration review. |
| Never store here | Real sleeps, network/model downloads or claims of statistical accuracy. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Future focused cases

Use injected monotonic/UTC clocks rather than sleeping. Check command cache fingerprints/eviction, independent revisions/state versions, text NFC/word-versus-letter joining, limits, expiry and content-free tombstones. Word-gate traces cover hold once, valid repeated segment, low-score versus neutral, freshness and interruption; parallel confirms and Clear cache purges retain atomic authority. These are acceptance descriptions only.
