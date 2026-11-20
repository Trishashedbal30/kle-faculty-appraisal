# KLE Faculty Appraisal — Start Here

This repository contains a local-first faculty appraisal prototype. The public checkout does not contain the supplied institutional source records, extracted seed, runtime databases, or demo credentials. Start with the synthetic sandbox.

## 1. Create a Python environment

Python 3.12 is the project target:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On Linux/macOS, use `python3.12 -m venv .venv` followed by `.venv/bin/python -m pip install -r requirements.txt`.

## 2. Run the synthetic demo

```powershell
# Set KLE_DEMO_PASSWORD in this process environment before starting the demo.
.\.venv\Scripts\python.exe manage.py demo
```

Set `KLE_DEMO_PASSWORD` to a private value of at least 12 characters in your local process environment before running the command. The sample values in [`.env.example`](.env.example) are placeholders; the application does not automatically load `.env` or write the password to disk. Open `http://127.0.0.1:8001`. Follow [the demo walkthrough](docs/DEMO_WALKTHROUGH.md); the sandbox does not modify the main application database.

## 3. Run the application with authorized institutional data

This path requires source documents that are deliberately not distributed. Only use files you are authorized to process:

```powershell
# Copy approved inputs into data/source/ locally; do not commit them.
.\.venv\Scripts\python.exe app\importer.py
.\.venv\Scripts\python.exe manage.py setup
.\.venv\Scripts\python.exe manage.py run
```

The importer creates `data/seed.json`, which is ignored by Git. Setup creates the local database and prompts for an administrator password. Read [data handling](docs/DATA_PROVENANCE.md), [operations](docs/OPERATIONS.md), and [security limitations](SECURITY.md) before processing real records.

## 4. Validate changes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe manage.py mcp-check
node --check web\assets\app.js
```

The private-source reconciliation test is skipped when `data/source/` is absent. See [the full README](README.md) for architecture, configuration, CI, and contribution guidance.
