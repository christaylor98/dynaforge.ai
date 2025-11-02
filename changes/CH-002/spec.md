# Spec — CH-002 (MS-01 Phase 1 Core Loop Refresh)

## 1. Overview
- Refresh and extend the Phase 1 core loop using the updated Phase 0 foundation from CH-001.
- Ensure WS-101, WS-102, WS-103, WS-104, WS-106, and WS-109 produce deterministic, auditable evidence.

## 2. Deterministic Inputs
- Seed: `MS01-P1-2025-11-03` (pending finalization)
- Branch: `feature/MS-01-Minimal-Agent-Loop`
- Environment prerequisites: `pytest` (if available), `python3`, access to `pipelines/` scripts, updated Phase 0 artifacts.

## 3. Workstream Breakdown
| WS | Requirements | Deliverables | Notes |
| --- | --- | --- | --- |
| WS-101 Multi-Agent Orchestration | FR-01, FR-04, FR-06 | Re-run orchestrator, updated `artifacts/phase1/orchestration/` bundle, refreshed approvals. | Use CH-001 docs as baseline; update `docs/PROJECT_OVERVIEW.md` as needed. |
| WS-102 Concern Lifecycle | FR-07 | Integration demo raising/updating/resolving concerns with Markdown + audit logs. | Store results under `artifacts/phase1/concerns/`. |
| WS-103 Human Approval Gates | FR-10 | New approval artifacts showing gate compliance and `/approve` flows. | Provide run log + summary in `docs/PROJECT_DETAIL.md`. |
| WS-104 QA Policy Enforcement | FR-11 | CLI/automation that enforces QA policy before Package. | Implement command/hook; capture results in `tests/results/CH-002.json`. |
| WS-106 Status Snapshots | FR-13 | Snapshot script/tool capturing stage + metrics for MS-01. | Output to `artifacts/phase1/status/`. |
| WS-109 Implementer Micro-Loop & Retention | FR-04, FR-27, FR-29 | Retention automation + micro-loop updates per CR002. | Document in `docs/IMPLEMENTATION_PLAN.md` and `TRACEABILITY.md`. |

## 4. Task List Overview
- Detailed tasks listed in `changes/CH-002/tasks.md` with owners and acceptance criteria.
- Implementer executes tasks sequentially while logging manifests.
- Tester validates orchestrator, concern lifecycle, QA enforcement, and snapshot outputs.

## 5. Acceptance Evidence
- Updated orchestrator run logs with approvals.
- Concern lifecycle run artifacts and Markdown sync proof.
- QA enforcement CLI run showing block/resume behavior.
- Status snapshot output with documented diff.
- Retention logs capturing implementer automation.
- Traceability updates reflecting new evidence.

## 6. Risks & Mitigations
- Missing dependencies (pytest) → Mitigation: fallback to `python3 -m unittest` with documentation of impact.
- Orchestrator drift → Mitigation: use deterministic seed, log manifests.
- QA enforcement blocking change → Mitigation: ensure enforcement can be toggled for testing with documented waiver process.

## 7. Handoff
- Spec + tasks now ready for Implementer after Human PM approval.
