# CI tooling tests

Owner: Hisham. This directory contains executable regression tests for the repository
checker introduced by the GitHub Actions task. Application test areas remain placeholders.

| Boundary | Responsibility |
|---|---|
| Receives | Synthetic text files and temporary local Git repositories |
| Produces | Standard-library unittest evidence that CI catches invalid input |
| Consumers | `.github/workflows/ci.yml`, maintainers running local checks |
| Never store here | User transcripts/tokens, real recordings, datasets or model binaries |

`test_repository_checks.py` covers syntax failures without executing Python, strict JSON,
Unicode/encoded paths, broken links/images, documentation examples, symlinks, ignore
protections, missing structure and files force-added despite `.gitignore`. Git staging in
these tests occurs only in disposable temporary repositories; no commits are created.

From the repository root:

```sh
python3 -B -m unittest discover -s tests/ci -p 'test_*.py' -v
```

No package install, model runtime, browser, camera or network access is needed by the tests.
