# Departmental pilot operating guide

## Roles

| Role | Responsibilities |
|---|---|
| Administrator | Verify identity/aliases, create/deactivate named accounts, retain source files; no automatic power to approve an appraisal |
| Faculty | Own records only; upload evidence, link activities, grant/revoke source consent, declare completeness, create/lock plans, run appraisals and appeal released reports |
| HoD | Review source evidence, inspect readiness, run faculty-locked batches, endorse reports after quality review, resolve appeals |
| Dean / IQAC | Review evidence, approve scoring policy, initial quality review, final release, inspect audit and restore approved versions |

Use separate named accounts for real people. Sandbox role accounts are solely for the isolated demonstration. Accounts are not tied to campus SSO in this package.

## Startup and shutdown

The server binds only to `127.0.0.1`. Use one Uvicorn worker for this SQLite pilot. Press Ctrl+C to stop. A failed run can resume from its saved checkpoint, provided its inputs are unchanged. A returned or stale plan should be revised rather than forced through.

## Passwords and accounts

No default password is supplied. Initial setup prompts for an administrator password. Other accounts are created under Access management; all passwords require at least 12 characters. Users can change their passwords from the account dialog; other sessions are invalidated. Deactivating an account revokes its sessions immediately. A deactivated faculty owner's plans cannot be launched as a batch.

## Backup and restore

Stop the server before backup so application data, graph checkpoints and files are consistent:

```bash
python manage.py backup backups/2026-10-11
```

The new backup folder contains the SQLite snapshot(s) and uploaded evidence. The `data/source/` directory is intentionally absent from the public repository. If authorized source files are present locally, back them up separately and protect them as confidential institutional records. Do not commit runtime databases, uploads, passwords, extracted seeds, or original personnel data to a public repository.

To restore, stop the server, retain a separate copy of the current runtime folder, then place the backed-up database files and `uploads` folder into `runtime/`. Run `python manage.py audit-check` before restarting. Never merge different checkpoint/app databases from different backup dates.

Report-version rollback in the UI is separate from database recovery: it changes the active approved version and preserves history.

## Campus deployment boundary

This deliverable runs on a local VS Code workstation. It has not been deployed to an institutional network. Before a shared institutional deployment, arrange HTTPS, set `COOKIE_SECURE=1`, configure institution-managed accounts/SSO as needed, review data-retention rules, protect filesystem access and backups, and test concurrency on the actual host. The current department-wide reviewer roles are not a multi-department authorization model. The optional MCP SSE listener rejects non-loopback bind addresses and only accepts a marked synthetic database under `runtime-demo/`, but its caller identity remains unauthenticated and callers can supply role/scope fields. Do not connect it to real data or external clients until that boundary is addressed. For larger deployments, migrate application/checkpoint storage to an appropriate managed database and add per-department scopes.

## Intake limitations

Added files are stored with hashes and require explicit activity links; arbitrary uploaded spreadsheets are not automatically parsed as institutional schema. The bundled importer targets the supplied workbook/PDF formats. To change a source integration, implement and test an adapter behind the connector. There is no live campus-system polling, email sending or autonomous external action.

## Troubleshooting

- `No module named ...`: install `requirements.txt` with the same `.venv` Python used to run the app.
- Port already in use: `python manage.py run --port 8010`.
- Python 3.14 package issue: use the tested Python 3.12 environment alongside your existing installation.
- No scoring policy: Dean/IQAC must upload, configure and approve the institutional rubric.
- Source consent missing: sign in as the owning faculty member and grant the relevant source; then create a new locked plan.
- Evidence stale: the record changed after verification. Have the reviewer verify the new record and create a new plan.
- PDF extraction warning about header: the supplied PDFs start with a leading newline before `%PDF`. They were parsed successfully; originals remain unchanged.
- Ollama absent: deterministic drafting remains available and clearly labelled. Check `OLLAMA_MODEL` and local Ollama service to enable model drafting.
- Report hidden: this is expected until the relevant quality-review stage. Faculty receive only the final approved release.
