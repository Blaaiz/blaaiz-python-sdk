# Releasing

This SDK uses [release-please](https://github.com/googleapis/release-please) to automate
releases. Nobody sets the version number by hand, writes the changelog entry by hand, or
creates a tag by hand.

## How a release works

1. Merge pull requests to `main` with [Conventional Commit](https://www.conventionalcommits.org/)
   messages:
   - `feat:` adds a feature and starts a minor release.
   - `fix:` fixes a bug and starts a patch release.
   - `feat!:`, or a commit with a `BREAKING CHANGE:` footer, starts a major release.
   - Only `feat`, `fix`, `perf`, and `revert` commits start a release. Other types, such as `docs:`,
     `test:`, `chore:`, and `ci:`, do not. release-please ignores a commit message that is not a
     Conventional Commit.
2. release-please opens or updates a pull request titled `chore(release): release X.Y.Z`. This
   pull request bumps every version string in the SDK and adds an entry to `CHANGELOG.md`.
3. Review the release pull request. Make sure that it changes only version strings and
   `CHANGELOG.md`, and that the latest CI run on `main` passed. Then merge it.
4. The workflow creates the tag `vX.Y.Z` and the GitHub Release.
5. The `publish` job publishes the package to PyPI.

## Rules

- Do not change the version number by hand.
- Do not create a tag or a GitHub Release by hand.
- Merge a pull request with **Create a merge commit**, and give it a plain title that is not a
  Conventional Commit. GitHub copies the title into the merge commit, and release-please reads a
  Conventional Commit title there as an extra changelog line.
- Do not squash-merge a pull request that has a plain title. release-please then ignores all of its
  changes.

## Keep the SDKs on one version

All Blaaiz SDKs (Node.js, Python, Laravel, Java) use the same version number for the same set of
features. To set a specific version instead of the next automatic one, add a `Release-As: X.Y.Z`
footer to a commit on `main`.

## Files that contain the version

release-please updates these files on every release:

- `pyproject.toml`
- `setup.py`
- `blaaiz/__init__.py`
- `blaaiz/client.py`
- `blaaiz/services/customer.py`
- `examples/flask_integration.py`
- `CHANGELOG.md`

Do not use `update_version.py` for a release. release-please does this work.

## Note on the release pull request

GitHub holds the CI runs of a pull request that GitHub Actions opens. To run CI on the release PR,
select **Approve and run** on it. The `publish` job does not run on a pull request. The release PR
changes only version strings, `.release-please-manifest.json`, and `CHANGELOG.md`. After you merge
it, CI runs on `main`, and the `publish` job waits for the tests to pass first.

## Required setup

1. Go to **Settings > Actions > General > Workflow permissions** for this repository.
2. Select **Allow GitHub Actions to create and approve pull requests**.

The `publish` job uses these repository secrets:

- `PYPI_API_TOKEN`

## If a job fails after the merge

release-please can create the tag and the GitHub Release in the same workflow run in which a test
fails. The `publish` job then does not run.

- If the failure is a flaky test or an outside problem, open the workflow run that created the
  release. Select **Re-run failed jobs**. The `publish` job then publishes the tagged commit.
- If the tagged code is broken, merge a fix. release-please then prepares the next patch release.

## Manual fallback

You can still publish a GitHub Release by hand for an existing tag. The `publish` job also runs
for a manually published release.
