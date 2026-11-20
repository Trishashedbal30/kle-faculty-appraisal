# Contributing

Thank you for helping improve KLE Faculty Appraisal. The project is a local pilot, not a deployed institutional service; contributions should preserve that boundary and avoid claims that have not been verified in code.

## Before you start

- Check existing documentation and tests before changing application behavior.
- Discuss changes that affect authorization, evidence decisions, scoring, approval order, storage, or data retention before implementing them.
- Do not use real faculty, student, institutional, or appraisal information in issues, pull requests, fixtures, screenshots, or tests. Use the existing synthetic demo fixtures.
- Do not add credentials, local databases, uploads, generated reports, the private source bundle, or its extracted seed/manifests.
- Preserve third-party attribution and confirm asset redistribution rights.

## Development setup

Use Python 3.12 and create a virtual environment from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On Linux/macOS, use `python3.12 -m venv .venv` and `.venv/bin/python`.

## Validation

Run the relevant checks before opening a pull request:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe manage.py mcp-check
node --check web\assets\app.js
```

The source reconciliation test is skipped when the unshipped private source bundle is absent. Do not copy private files into a contribution just to make that check run. The test suite and demo should remain synthetic and repeatable.

## Pull requests

- Explain the behavior change and any security/privacy implications.
- Include or update focused tests for behavior changes.
- Update directly affected docs and state validation limits accurately.
- Keep changes focused; do not reformat unrelated files.
- Inspect the staged diff for private data, secrets, generated files, and unrelated changes before submitting.

## Reporting issues

Use the issue templates for non-sensitive bugs and feature proposals. Do not submit vulnerability details or private institutional information in a public issue; follow [SECURITY.md](./SECURITY.md).
