# Lab execution guide

The capstone code composes the lab capabilities in one application. The implementation-to-lab mapping is in `docs/WORKLET_TRACEABILITY.md`.

- Lab 1: open `01_planner.ipynb`; enter a vague request, answer the clarification prompts and revise the plan.
- Labs 2–5: `python manage.py import-check`; inspect `contracts.py`, `skills.py`, `connector.py`, `memory.py`; use scoped evidence search in the UI.
- Labs 6–7: run the synthetic walkthrough; stop/restart during a review pause. The same run remains available.
- Lab 8: `python labs/08_benchmark.py`. This uses three synthetic faculty and explicitly simulated 100 ms source latency; it compares the real sequential/multi-unit LangGraph runs and checks score/check equivalence.
- Labs 9–12: `python manage.py test`; inspect the missing-evidence, consent, failure injection, immutable release and rollback tests.
- Lab 13: inspect `specialists.py`, configure a policy for the selected track and verify that mismatched policies are refused.
- Lab 14: follow `docs/DEMO_WALKTHROUGH.md`, then perform institutional acceptance with genuine consent, evidence and the approved rubric. The demo is not a substitute for that real-case sign-off.
