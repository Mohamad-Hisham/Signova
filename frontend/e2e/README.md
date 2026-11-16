# frontend/e2e

Owner: **Adham with Ali and Hisham**.

Future Playwright full-browser acceptance scenarios.

| Boundary | Responsibility |
|---|---|
| Receives | Controlled fake camera/transport, approved real fixtures later, supported browser matrix. |
| Produces | Future reproducible user journeys with cleanup/recovery evidence. |
| Consumers and dependencies | Frontend/backend release acceptance. |
| Never store here | Browser binaries, videos containing private sessions or claims that a static page proves device support. |

## Directory contents

| Entry | Purpose |
|---|---|
| `README.md` | This directory guide: owner, inputs/outputs, consumers, exclusions and child-file responsibilities. |

## Future browser journeys

Playwright scenarios should exercise create/auth/start/preview/confirm/edit/copy/TXT/clear/end/delete, hold/repeat, reconnect/refresh/offline removal, denied camera/clipboard/storage and cleanup during encoding. Use controlled fake media and later permitted real fixtures. Record the actual tested browser/device matrix; manually check device/permission/portrait behavior that automation cannot prove. No browser installation, test, build or video recording occurs now.
