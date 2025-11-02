# Spec — CH-001 (MS-01 Phase 0 Refresh)

## 1. Overview
- Purpose: regenerate the Phase 0 evidence required for MS-01 so the PM → Designer → Implementer → Tester loop can be demonstrated end-to-end with current artifacts.
- Scope boundaries follow the Frame brief (`changes/CH-001/brief.md`) focusing on WS-01, WS-02, WS-05, WS-07, and WS-08 entries in `TRACEABILITY.md`.
- Completion definition: refreshed assets satisfy FR-01, FR-02, FR-06, FR-09 notes in `TRACEABILITY.md` with deterministic evidence stored under `artifacts/work/CH-001/` and `tests/results/CH-001.json`.

## 2. Deterministic Inputs
- Planner seed: `MS01-P0-2025-11-02`.
- Codebase snapshot: `main` branch as of 2025-11-02 EDT; no additional migrations expected.
- Audit prefix: every log event must include `change_id="CH-001"` and `phase="0"`.

## 3. Workstream Alignment
| Workstream | Requirement focus | Deliverable Refresh |
| --- | --- | --- |
| WS-01 Repository Skeleton | FR-01, FR-02 | Update `docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_DETAIL.md`, ensure layout guidance matches regenerated runs. |
| WS-02 Audit Logging Primitives | FR-06, FR-09 | Regenerate audit logger demo (`audit/sample_handoff.jsonl`) and ensure `/status` `/clarify` events linked. |
| WS-05 Project Manager Skeleton | FR-01, FR-02, FR-10 | Re-run PM agent integration to update docs and handoff logs. |
| WS-07 Demo Workflow Target | FR-01, FR-06, FR-09 | Refresh `artifacts/phase0/demo/` bundle from new run seed. |
| WS-08 Documentation Updates | FR-02, FR-10 | Sync docs with regenerated evidence; capture approval placeholders. |

## 4. Deliverable Breakdown
1. **PM Run & Documentation Refresh**  
   - Execute PM agent orchestrator for Phase 0; capture outputs in `docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_DETAIL.md`, `docs/VERSION_CONTROL.md`.  
   - Update milestone note in `TRACEABILITY.md` if evidence paths change.
2. **Audit Logging Replay**  
   - Run audit logger sample script with new seed; store results in `audit/sample_handoff.jsonl` and `audit/handoff_ms01_phase0.jsonl`.  
   - Ensure commands emitted by interaction stub reference `CH-001`.
3. **Demo Bundle Regeneration**  
   - Execute `make demo` (Phase 0 mode if selectable) or equivalent script; stage output under `artifacts/phase0/demo/YYYY-MM-DD/`.  
   - Include README snippet describing run parameters.
4. **Documentation Sync**  
   - Update `docs/IMPLEMENTATION_PLAN.md`, `docs/PROJECT_OVERVIEW.md`, `docs/VERSION_CONTROL.md`, `docs/WORKFLOW.md` sections referencing Phase 0 evidence.  
   - Insert change log entry referencing CH-001 if applicable.
5. **Testing & Validation Prep**  
   - Define test commands for Tester (TC-FR01-001/002, TC-FR06-001, TC-FR08-001) and confirm prerequisites in repository.

## 5. Acceptance Evidence
- `artifacts/work/CH-001/run-*/manifest.json` summarizing commands, seeds, and outputs.
- `tests/results/CH-001.json` capturing pass status for required test cases.
- Updated documentation committed with CH-001 references and approval placeholders.
- Audit JSONL entries with timestamps on or after 2025-11-02 validating PM→Designer→Implementer→Tester handoffs.

## 6. Risks & Mitigations
- **Risk**: Missing deterministic flag for demo run causes drift.  
  *Mitigation*: Record command options and environment variables in run manifest.
- **Risk**: Docs accumulate stale links.  
  *Mitigation*: Implementer to grep for Phase 0 artifact paths during Execute stage and update accordingly.

## 7. Handoff
- Spec + tasks delivered to Implementer pending Human PM approval.  
- Await `/approve CH-001` on Spec stage before execution proceeds.
