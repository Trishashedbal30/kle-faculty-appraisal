# Validation record

## Local checks completed for repository preparation

| Check | Result |
|---|---|
| `python -m pytest -q` | **36 passed** in 183.93 seconds using the configured local Python 3.14 environment, with the supplied local source bundle present |
| `node --check web/assets/app.js` | Passed; no syntax errors |
| `python manage.py mcp-check` | Passed; completed MCP tool discovery for five tools |

The locally configured interpreter was Python 3.14. The project documentation and GitHub Actions workflow target Python 3.12; the local run is not a substitute for the CI run on 3.12.

## Test coverage represented by the suite

The tests exercise synthetic workflow setup, authentication and authorization behavior, evidence/consent gates, policy validation and arithmetic, checkpoint recovery, bounded repairs, batch processing, report release, appeals, rollback, and audit integrity. Test fixtures use synthetic records.

One source-reconciliation test inspects the separately supplied private XLSX/PDF files. It runs when that local bundle exists and is skipped when the private `data/source/` directory is absent from a clean public checkout. The test is not replaced with a passing assertion; its source-dependent checks still run whenever those files are available.

## Not validated here

- Python 3.12 execution in this local environment; CI is configured to perform that check.
- Browser rendering and repeatable browser automation across Windows, Linux, and macOS.
- A live Ollama model or semantic embeddings.
- External identity/SSO, network deployment, production concurrency, or institutional policy.
- Security of MCP caller identity; the optional MCP server currently accepts caller-provided role/scope values.
- A real faculty appraisal or institutional approval.

The real-data importer can be checked only with authorized local source files. Do not add those files to CI or the public repository.
