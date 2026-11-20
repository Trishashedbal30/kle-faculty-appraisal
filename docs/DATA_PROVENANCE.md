# Data provenance and local handling

## Distribution boundary

The original XLSX/PDF records, roster images, extracted `data/seed.json`, and source/package manifests are intentionally excluded from the public Git repository. The source bundle contains identifiable institutional material and appraisal-related records. Runtime databases, uploaded evidence, generated reports, and demo credentials are also local-only.

The existing files are not deleted or modified by repository preparation. The ignore rules only prevent untracked copies from being added to Git. If these files have ever been committed elsewhere, remove them from that repository's history and follow the institution's incident and retention procedures; adding an ignore rule does not erase prior commits.

## Import behavior

`app/importer.py` extracts records from supported local XLSX and PDF inputs and records source checksums and locators. It preserves source fields for traceability and does not independently verify identity, publication metadata, or the institutional validity of an appraisal claim.

To use the real-data path, obtain authorization for the source files, place them in `data/source/`, run `python app/importer.py` to create the ignored seed, and then run `python manage.py setup`. Keep the source files and generated seed on a controlled local system. `python manage.py import-check` can inspect a local source bundle without writing the seed.

## Synthetic demo

`python manage.py demo` provisions a separate synthetic sandbox under `runtime-demo/` and requires `KLE_DEMO_PASSWORD` from the local process environment. The database, checkpoints, and uploads are excluded from source control; the password is not written to a file. The synthetic training rubric is not an institutional policy and must never be represented as one.

## Review responsibilities

- Confirm faculty identity and aliases using authoritative records; normalized text matches are candidates, not proof.
- Inspect each source and locator before recording an evidence decision.
- Confirm period, authorship, source quality, and applicable consent with the institution.
- Use only the institution-approved policy and record its cited authority.
- Do not infer missing activity from an incomplete source or treat imported claims as verified.
- Protect backups, local databases, uploads, and reports as confidential information.

For the implemented trust boundaries and deployment limits, see [architecture](./ARCHITECTURE.md), [policy configuration](./POLICY_CONFIGURATION.md), and [operations](./OPERATIONS.md).
