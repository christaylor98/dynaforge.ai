# Task List — CH-002

| Task ID | Stage | Owner | Description | Deliverables | Acceptance Notes |
| --- | --- | --- | --- | --- | --- |
| T-001 | Execute | Implementer | Re-run Phase 1 orchestrator with seed `MS01-P1-2025-11-03`, regenerate logs/approvals. | `artifacts/phase1/orchestration/run-2025-11-03/`, updated docs references. | Orchestrator log captures PM→Designer→Implementer→Tester handoffs; approvals recorded. |
| T-002 | Execute | Implementer | Produce concern lifecycle integration demo (raise/update/resolve). | `artifacts/phase1/concerns/run-2025-11-03/`, Markdown sync evidence. | End-to-end flow mirrored in docs and audit JSONL. |
| T-003 | Execute | Implementer | Implement QA enforcement CLI and integrate into Validate stage. | CLI script/module, `tests/results/CH-002.json` showing enforcement. | QA enforcement blocks promotion until tests pass or waiver logged. |
| T-004 | Execute | Implementer | Add status snapshot tooling for Phase 1. | `artifacts/phase1/status/snapshot-2025-11-03.json`, doc updates. | Snapshot demonstrates stage status and metrics. |
| T-005 | Execute | Implementer | Update implementer micro-loop and retention automation per CR002. | Scripts/configs, retention log entries, doc updates. | Retention obeys `retain` markers & auto-purges per policy. |
| T-006 | Validate | Tester | Validate orchestrator rerun, concern lifecycle, QA enforcement, snapshot outputs. | `tests/results/CH-002.json`, QA summary update. | All relevant tests pass; QA enforcement verified. |
| T-007 | Package | PM Agent | Update docs (`PROJECT_OVERVIEW.md`, `PROJECT_DETAIL.md`), traceability, demo collateral. | Updated docs, `TRACEABILITY.md`, demo summaries. | Documentation reflects Phase 1 refresh; approvals captured. |
| T-008 | Cleanup | Governance | Log retention, close workspace, archive evidence. | `audit/retention.jsonl`, `changes/CH-002/status.md` closed. | Workspace closure recorded; no open concerns. |
