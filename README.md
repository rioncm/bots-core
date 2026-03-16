# bots_core

`bots_core` is the standalone repository folder for the extracted `botscore`
translation runtime.

Repository name and Python package name are intentionally different:

- repository folder: `bots_core`
- distribution name: `botscore`
- import package: `botscore`

`botscore` contains the extracted Bots translation runtime:

- grammar loading
- parsing into message trees
- mapping execution
- serialization

It intentionally excludes the larger legacy Bots application surface such as:

- Django admin and web UI
- engine orchestration
- routes and channels
- database-backed business configuration
- `usersys` as a required runtime convention in the supported path

## Local development

```bash
pip install -e .[dev,test]
pytest
python -m build --wheel --sdist --no-isolation
```

## Versioning

`botscore` is versioned independently from `bots_airflow`.

The intended rule is:

- `botscore` versions describe runtime compatibility for grammar loading, parse/tree,
  mapping execution, and serialization
- downstream packages such as `bots_airflow` declare compatible version ranges
- releases use semantic versioning

## Release tags

Because `botscore` now lives in its own repository, standard tags are sufficient:

```text
v0.1.0
```

## PyPI publishing

This repository publishes `botscore` to PyPI through GitHub Actions Trusted Publisher.

The release flow is:

1. push a release tag such as `v0.1.0`
2. the `publish.yml` workflow builds wheel and sdist artifacts
3. the workflow validates metadata with `twine check`
4. GitHub publishes to PyPI through the `pypi` environment
