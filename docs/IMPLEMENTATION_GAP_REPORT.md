# Implementation Gap Report and L1–L14 Traceability

This report distinguishes executable evidence from code inspection and browser-only checks. A documentation statement is not treated as proof of a feature.

## Latest verification evidence

Executed from the project root using the configured local Python environment:

| Command | Result |
|---|---|
| `python -m pytest -q tests/test_reliability.py::test_three_collection_agents_execute_concurrently tests/test_governance.py::test_new_faculty_activity_runs_through_governed_release_history tests/test_governance.py::test_frontend_asset_wires_the_complete_appraisal_workflow` | Exit 0; `3 passed in 16.21s` |
| `python -m pytest -q` | Exit 0; `36 passed in 183.93s` using the local Python 3.14 environment |
| `node --check web/assets/app.js` | Exit 0; no syntax errors reported |
| `python manage.py mcp-check` | Exit 0; MCP tool discovery completed (`count: 5`) |

An initial version of the new intake-to-publication test failed because its assertion used `id` instead of the report schema's `record_id`; the assertion was corrected, and the focused test and full suite then passed. This was a test assertion error, not a production workflow failure.

## Browser verification and limits

Using the installed VS Code browser session against an isolated synthetic demo server, I exercised the served SPA:

- Dean signed in and approved the synthetic-only policy.
- Faculty uploaded a synthetic evidence file, submitted an activity, and granted consent for all four relevant sources.
- HoD signed in and verified all four activity records through the evidence-review form.
- Faculty created and locked a plan, then started a run.
- Dean, HoD, and IQAC each signed in separately and approved their assigned review stage. The report appeared as released only after the final IQAC decision.
- Faculty opened Reports & appeals and submitted an appeal; IQAC resolved it, used Restore version, and viewed the verified audit trail.

The browser's download event was not observable through the integrated browser tool. PDF response generation is verified by the automated API test (`%PDF` response check), and the SPA's report list exposes the export link. Browser automation is not configured as a repeatable project test suite; the browser run above was interactive/tool-driven and used only synthetic data. The temporary server and its isolated synthetic database were stopped and removed.

## L1–L14 traceability matrix

| Lab | Implementation files | Executable evidence | Status |
|---|---|---|---|
| L1 — Clarify, plan, revise | `app/main.py`, `app/contracts.py`, `app/skills.py`, `web/assets/app.js` | `test_new_faculty_activity_runs_through_governed_release_history`; `test_checkpoint_survives_runtime_recreation` | PASS |
| L2 — Tools and computation | `app/connector.py`, `app/scoring.py`, `app/store.py` | `tests/test_data_and_scoring.py`; new intake-to-publication test checks a nonzero approved-policy score | PASS |
| L3 — Reusable skills | `app/skills.py`, `app/workflow.py` | Full journey executes plan/report assembly; `test_targeted_repair_after_injected_citation_fault` | PASS |
| L4 — Memory and persistent state | `app/store.py`, `app/memory.py`, `app/workflow.py` | `test_scoped_memory_obeys_consent`; `test_checkpoint_survives_runtime_recreation` | PASS |
| L5 — MCP connector | `app/mcp_server.py`, `app/mcp_client.py`, `manage.py` | `tests/test_mcp_smoke.py`; `manage.py mcp-check` completed a real stdio MCP tool-discovery round trip | PASS |
| L6 — Controlled runtime, retry, audit | `app/workflow.py`, `app/store.py`, `app/security.py` | `test_bounded_retry_on_unrepairable_output`; `test_audit_tamper_detection`; `test_resume_after_actual_node_failure` | PASS |
| L7 — LangGraph workflow | `app/workflow.py`, `app/main.py` | `test_checkpoint_survives_runtime_recreation`; `test_resume_after_actual_node_failure`; new intake-to-publication test exercises review interrupts | PASS |
| L8 — Parallel collection and merge | `app/workflow.py`, `app/batch.py` | `test_three_collection_agents_execute_concurrently` synchronizes the three category collectors with a barrier; `test_batch_runs_two_units_and_merge` | PASS |
| L9 — Research, teaching, service collection | `app/connector.py`, `app/workflow.py`, `app/main.py` | `test_new_faculty_activity_runs_through_governed_release_history` validates new administrative intake plus seeded research/teaching/service collection | PASS |
| L10 — Evidence validation and API scoring | `app/workflow.py`, `app/scoring.py`, `app/contracts.py` | `test_missing_consent_hard_gate`; `test_missing_evidence_hard_gate`; `test_changed_source_blocks`; `test_stale_evidence_and_no_matching_rule`; full intake-to-release test | PASS |
| L11 — Human approvals and authorization | `app/main.py`, `app/security.py`, `web/assets/app.js` | New intake-to-release test asserts no release before each required stage and verifies Dean → HoD → IQAC; `test_csrf_and_role_permissions`; non-faculty activity submission returns 403 | PASS |
| L12 — Report and export | `app/reports.py`, `app/main.py`, `web/assets/app.js` | `test_end_to_end_gate_export_and_rollback` and new journey check PDF starts with `%PDF`; browser opened report list (download event not captured) | PASS (API); browser download not independently captured |
| L13 — Versioning, appeals, rollback | `app/main.py`, `app/store.py`, `web/assets/app.js` | New intake-to-release test creates versions 1 and 2, appeals/resolves, rolls back to v1 and verifies active version and audit; browser exercised appeal/resolve/rollback controls | PASS |
| L14 — Full system integration and demo | `web/`, `app/main.py`, `app/demo.py`, `manage.py` | `test_frontend_asset_wires_the_complete_appraisal_workflow`; 36-test suite; interactive browser journey through SPA and synthetic roles | PARTIAL — no repeatable browser automation suite; only `labs/01_planner.ipynb` and `labs/08_benchmark.py` are present as direct lab artifacts |

## Implemented change and remaining limits

- Activity submission is now faculty-only in both the API and the UI. Reviewer accounts cannot create claims on a faculty member's behalf through `/api/activities`.
- The UI shows Add activity only for faculty. Existing role checks for consent, evidence decisions, plan locking, approvals, publication, appeal resolution, rollback, and audit access remain server-enforced.
- The API integration test covers upload → activity → consent → HoD verification → locked plan → validated scoring → Dean/HoD/IQAC approvals → publication → version 2 → PDF export → appeal → resolution → rollback → audit integrity.
- The frontend test checks the served SPA assets and required action/API wiring. It does not replace automated browser interaction coverage.
- No dedicated Playwright/Selenium project configuration or CI browser run exists. A reproducible browser automation suite remains the main gap. The manual integrated-browser exercise covered the real UI path with synthetic records but is not a committed automated test.
- The project contains direct lab artifacts for only L1 and L8; the remaining lab traceability above maps application code and executable tests, not separate lab notebooks.
