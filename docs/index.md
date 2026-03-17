# bots_core Docs

`bots_core` packages the extracted `botscore` translation runtime as a standalone
Python distribution.

Current pages:

- [API Reference](reference.md)

Current scope:

- grammar loading
- parsing into message trees
- mapping execution
- serialization

The supported runtime intentionally excludes the broader legacy Bots application
surface such as Django admin, engine orchestration, routes and channels, and
database-backed business configuration.

## Local development

```bash
pip install -e .[dev,test,docs]
pytest
mkdocs serve
```

## Package identity

- repository folder: `bots_core`
- distribution name: `botscore`
- import package: `botscore`
