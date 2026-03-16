# GitHub Actions Workflows

This directory contains the validation and publishing workflows for `botscore`.

## `ci.yml`

Runs on pull requests and pushes to the main branches.

Jobs:

- `test`
  Installs the package with dev and test dependencies, runs Ruff, and executes the
  standalone `botscore` test suite.
- `build`
  Builds the source distribution and wheel for `botscore`.

## `publish.yml`

Runs on version tags like `v0.1.0` and on manual dispatch.

Jobs:

- `build`
  Builds the `botscore` source distribution and wheel, validates them with
  `twine check`, and uploads them as an artifact.
- `publish-pypi`
  Publishes the uploaded distributions to PyPI using GitHub Trusted Publisher.

Expected Trusted Publisher configuration:

- repository: `rioncm/bots-core`
- workflow file: `.github/workflows/publish.yml`
- environment: `pypi`
