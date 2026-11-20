# Worklet 8: fourteen-lab traceability

The supplied specification is preserved in `data/source/Pasted text(20261011-041417).txt`. This table distinguishes implemented capabilities from acceptance requiring actual institutional input or deployment.

| Lab | Implementation and runnable evidence | Acceptance status |
|---|---|---|
| 1. Agent vs chatbot | `labs/01_planner.ipynb`; `/api/planner/clarify`; editable plan followed by explicit lock | Vague input produces at least two questions. A revised plan receives a new identity. |
| 2. Typed tools | `Connector`, `PlanInput`, `PolicyInput`, deterministic `compute`; real XLSX/PDF extraction | Source reconciliation and independently checked weighted-mean arithmetic are tested. No prompt-generated API numbers. |
| 3. Reusable skills | `plan_skill` and `format_skill`; typed input contracts and typed shared state | Used unchanged by multiple synthetic faculty in the batch test. |
| 4. Memory and retrieval | Separate checkpoint and repository databases; category-filtered retrieval and archive history | Scoped/consented retrieval tested. Local lexical embedding similarity works without a model; Ollama semantic embeddings are optional and not live-model tested here. |
| 5. One governed connector | Authenticated REST endpoints and `Connector` source interface; optional stdio/SSE MCP server | REST access, consent, source integrity and cross-faculty rejection are tested. MCP SSE is restricted to loopback binds, but the server does not authenticate caller identity; use only with synthetic data until that boundary is secured. |
| 6. Governed runtime | Node budgets, audit input/output references, persisted graph checkpoints and resume | Actual injected node crash and runtime recreation tests pass. No production crash/chaos campaign is claimed. |
| 7. Explicit agent graph | `StateGraph`, typed state, three collectors, join, validation, score, report, retry and interrupt gates | Complete synthetic run reaches and pauses at each real human gate. |
| 8. Parallel units and merge | Three collection branches; up to ten locked plans, three concurrent unit workers; deterministic alignment selector | Two-unit integration test and reproducible three-unit latency benchmark. No real-campus throughput claim. |
| 9. Grounding | Per-claim file hash and locator, human evidence decision, original record hash, component citations | Missing, stale and changed-file evidence blocks calculation; source rows reconcile to supplied originals. |
| 10. Self-healing | Targeted citation restoration/arithmetic recomputation; maximum two repairs; explicit source-failure escalation | Injected citation fault repaired; unrepairable scope fault stops after two attempts. |
| 11. Spec to tested output | Locked plan fingerprint, approved policy hash, acceptance checks before review; automated suite | Synthetic acceptance and negative paths tested; real-case acceptance awaits official rubric and evidence decisions. |
| 12. Safety/governance | Role/scope checks, consent, three human gates, versions, appeals, rating overrides and rollback | Publication bypass, confidentiality, revoked consent, repeat decisions, appeals, audit tampering and rollback tested. |
| 13. Specialists | `specialists.py` registry; balanced, teaching, research and administrative tracks | Deterministic grounded emphasis; policy must match chosen track. No unapproved reweighting. |
| 14. Capstone | Runnable local server, dashboard, imported real snapshots, PDF export, operating guide and synthetic end-to-end demonstration | **Local implementation delivered. Actual team-owned college deployment and real-person committee sign-off remain institutional acceptance tasks.** |

## Guardrail interpretation

The worklet both mentions sharing drafts early and later says that an API score/report must not be released to faculty or HoD without IQAC/Dean review. The application implements the stricter rule: faculty can see input records, plans, readiness and exceptions; only Dean/IQAC sees the initial calculated draft. The HoD receives it after quality review. Faculty receives a report only after final release.

The user can approve, document a valid-band rating override, or return a report with correction instructions. Editing an evidence claim or policy requires a new plan/run so previous approvals cannot silently apply to changed numbers. Review notes and overrides remain visible to subsequent authorities and in the final approval trail.

## Definition-of-Done prerequisites not present in the attachments

- The actual approved institutional API rubric, rating bands, permitted rounding/caps and track rules.
- Real source consent and verified identity/account binding by the institution.
- Evidence for activities beyond the supplied publication/feedback snapshots, or truthful complete-cycle nil declarations where appropriate.
- Named HoD/Dean/IQAC review and sign-off on an actual case.
- Institutional hosting, operational ownership, backup policy and security acceptance.

These prerequisites are hard-gated or documented. No real faculty member has been given an invented API score, consent, verification or approval to make the initial dashboard look complete.
