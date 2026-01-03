Authorized AI Execution Framework — Presentation Notes

Overview
- Purpose: Enforce pre-execution authorization and runtime constraints for AI systems.
- Core Principle: No implicit behavior — every capability must be explicitly declared, verified, and enforced.
- Architecture: Specification layer → Static verification → Constrained runtime enforcer.

Key Contributions (for professor)
- Deterministic pre-execution verification that rejects underspecified or unsafe specs.
- Runtime enforcement via `MonitoredContext` that halts on unauthorized access/action.
- Clear separation of concerns: spec, verification, runtime.
- Designed for research: extensible checkers, auditable logs, and safe-by-default behavior.

Demo Summary
- Test 1 (Compliant): Reads `users_table` and performs allowed `read` action — execution succeeds.
- Test 2 (Violating): Attempts to read `passwords_table` — runtime enforcement raises a `RuntimeViolation` and execution is stopped.

Design Decisions to Emphasize
- Explicit `ForbiddenPattern` and `ExecutionScope` types.
- `CompletenessChecker` enforces explicit lists (no `None`).
- Conservative defaults in `ExecutionScope` but explicit validation prevents implicit allowances.
- Audit logging in `VerificationOrchestrator` for reproducibility and grading.

Suggested Talking Points for Presentation
- Explain motivation: accidental or implicit AI capabilities cause real-world harm.
- Walk through the spec creation (show `demo/run_demo.py`).
- Demonstrate verification logs and runtime enforcement output.
- Discuss extensibility: add new checkers, richer forbidden-pattern matching, or integrated auditing storage.

Next Steps (research roadmap)
- Add pattern-based forbidden-data matching (regex, schema diff).
- Add resource tracking (memory, I/O) to `MonitoredContext`.
- Integrate reproducible audit trails (append-only log or DB) and export formats for compliance.
- Design user studies to evaluate whether specification style helps human reviewers catch unsafe specs.

Contact / Notes
- Code location: `src/` (run with `PYTHONPATH=src python3 -m demo.run_demo`).
- Ask if you'd like a short slide deck created from these notes.
