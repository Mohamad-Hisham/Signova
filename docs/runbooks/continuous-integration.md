# Continuous integration and how to verify it

Owner: Hisham, with module-owner review when application suites are added.
Inputs: a branch push, PR targeting main, optional main merge group or manual dispatch.
Output: **Repository checks**, a job in **Signova CI**. Never provide real credentials,
camera media, transcripts, datasets or model weights to these checks.

The later GitHub Actions task authorizes executable CI tooling and its regression tests.
Frontend, backend, data and model application modules remain comment-only. The workflow
has been validated locally; a hosted run must be verified after you push these files.
No commit, push or GitHub settings change is made by the authoring task.

## What runs

| Event | Revision checked |
|---|---|
| Push to any branch, including main | That pushed branch revision |
| PR opened, updated, reopened, ready for review or edited, targeting main | GitHub's combined PR/main merge revision |
| PR merged into main | The resulting main revision, through the push trigger |
| Optional merge queue targeting main | The merge-group revision |
| Manual Run workflow | The selected branch revision; dispatch becomes available after the workflow exists on the default branch |

This preserves checkout's default PR merge ref; overriding it with the PR head would
lose the combined-main check. A branch push and its open PR can create two runs;
they validate different revisions. Newer runs cancel older ones for the same event/ref.
The workflow has no path filters, so documentation-only PRs still get the required check.
PR merge conflicts must be resolved before GitHub can run the combined revision.
See [GitHub's workflow event documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

The five steps check out code, select Python 3.11, show the tested commit, run CI-tooling
regression tests, then run repository validation. The job has read-only contents access,
no retained checkout credential, a five-minute timeout and no project dependency install.
Official action pins were verified against
[checkout v6.0.2](https://github.com/actions/checkout/releases/tag/v6.0.2) and
[setup-python v6.1.0](https://github.com/actions/setup-python/releases/tag/v6.1.0).
Review release identity before updating their full SHA pins.

Repository validation covers Python syntax without running/importing application code,
strict JSON including duplicate/nonfinite values, inline local Markdown links/images,
major module guides, representative ignore protections, and accidentally tracked files
that match `.gitignore`. Local additions are included without requiring staging.
External URLs, Markdown anchors/reference-style links, TypeScript types, dependencies,
runtime behavior and complete secret scanning are outside this check's scope.

## 1. Run the exact checks locally

From the repository root, with Python 3.11 and Git available:

```sh
python3 -B -m unittest discover -s tests/ci -p 'test_*.py' -v
python3 -B scripts/check_repository.py
```

Expected: the regression tests end in `OK`, and validation prints `Repository checks
passed`. Both commands exit with code 0. No package installation is needed. If a tracked
file was intentionally deleted, stage that deletion so local Git file discovery agrees
with the intended next checkout. Ignored local environments/media are skipped.

## 2. Verify a branch push and PR

1. Review `git status` and your diff, create a feature branch such as `ci/verify-actions`,
   commit the CI/doc changes, and push that branch yourself. Do not force-add ignored data.
2. On GitHub, open **Actions → Signova CI**. Find the run with event **push** and that
   branch/commit. **Repository checks** should turn green. Inspect each step's logs.
3. Open a PR from that branch into **main**. Its Checks tab should show another green
   **Repository checks** result with event **pull_request**.
4. Open **Show the tested commit** in that PR run. It should show GitHub's synthetic
   merge commit, rather than only your feature branch head. The push run shows the branch
   commit. This distinguishes the two checks without implementing any app feature.

If no run appears, check the workflow file is pushed, the PR targets main, Actions are
enabled in repository settings, and your policy permits the two official actions.
Fork-contributor runs may need maintainer approval. Review the failed step's first error
before retrying; re-running an unchanged invalid revision will fail again.

## 3. Prove a failing change is caught

Use the disposable feature branch/PR, never a direct main change. Create
`ci-negative-test.json` in the repository root containing exactly:

```text
{"broken": }
```

Run the local checker: it must exit 1 with an `invalid JSON` diagnostic. Commit and push
that temporary file yourself. The branch push and PR runs should both fail. This is
deliberately invalid metadata, not a secret, camera fixture or application implementation.

Fix its contents to the valid JSON below, commit and push the fix:

```json
{"fixed": true}
```

Both new runs should pass. Remove the temporary file in another commit before merging
the CI PR. Keep the useful CI/doc changes. The automated checker tests also exercise
broken Python/links and force-tracked ignored files entirely in disposable local folders;
there is no reason to push sensitive files to test the policy.

## 4. Verify the actual main update and manual trigger

After the PR is green and reviewed, merge it. Open Actions and verify a new **push** run
for **main** with the resulting main commit passes. This tests the actual merged code.
Do not close an unmerged PR and expect the same main run. A failed post-merge check is
visible evidence to investigate; CI does not automatically revert main.

Once the workflow is on the default branch, Actions → Signova CI → **Run workflow** →
choose main → run. The new event should be **workflow_dispatch** and pass the same job.
The merge-group trigger is exercised only if the repository uses a merge queue.

## 5. Make the check required before merging

A workflow reports results; a branch rule is needed to block failing merges. After the
check has run, configure a main branch protection/ruleset in GitHub repository settings:

- Require a pull request before merging.
- Require status checks, selecting **Repository checks** from **GitHub Actions**.
- Require the branch to be up to date before merging, or use the repository's merge queue.
- Apply the intended administrator/bypass policy for the team.

On the intentionally failing PR, confirm merging is blocked. After fixing it, verify the
check is satisfied; other review rules may still apply. Availability depends on repository
plan/settings. No branch rule is changed by adding this workflow. See
[GitHub's protected branch documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

## Adding application tests later

This CI is useful today but does not claim API/UI/model coverage. When actual implementation
and tested locks exist, add jobs for frontend `npm ci` plus agreed type/lint/Vitest/build
commands; backend tested dependencies plus Ruff/Pytest; then Playwright/integration as
appropriate. Use explicit jobs and fail real tests rather than silently skipping missing
commands with `--if-present`, `|| true` or `continue-on-error`. Keep model training, private
datasets and large weights out of default PR CI. Record new required job names and exact
local commands here. Preserve the branch push, combined-main PR and post-merge triggers.
