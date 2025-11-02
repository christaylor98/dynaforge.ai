# Change Brief — CH-001 (MS-01 Phase 0 Refresh)

## Objective
- Rebuild the MS-01 Phase 0 foundation so the PM → Designer → Implementer → Tester loop has fresh evidence for the POC spike described in `docs/WORKFLOW.md`.
- Restore the minimum agent chain artifacts that were marked `CHANGE IMPACTED` or `PARTIAL` in `TRACEABILITY.md` for Phase 0 workstreams (WS-01, WS-02, WS-05, WS-07, WS-08).

## Scope
- Update repository skeleton documentation and linked PM deliverables to satisfy FR-01 / FR-02 expectations (`TRACEABILITY.md` rows for WS-01 and WS-05).
- Regenerate audit logging primitives and sample outputs needed for FR-06 / FR-09 (`TRACEABILITY.md` rows for WS-02 and WS-07).
- Refresh demo collateral under `artifacts/phase0/demo/` so it reflects the latest orchestrated run (`TRACEABILITY.md` WS-07 notes).
- Ensure human-facing docs (`docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_DETAIL.md`, `docs/VERSION_CONTROL.md`) match the regenerated evidence per WS-08.

## Out of Scope
- Governance automation and maturity-level gates beyond the minimal MS-01 expectations.
- Phase 1+ enhancements (e.g., expanded approval routing, retention policy automation) except where required to unblock Phase 0 deliverables.

## Acceptance Criteria
- Phase 0 workstreams report regenerated evidence with links captured in `TRACEABILITY.md`.
- Audit and demo artifacts replay the PM → Designer → Implementer → Tester sequence end-to-end with deterministic output.
- Documentation referenced in FR-01/FR-02/FR-06/FR-09 is current and approved by the human PM.
- Handoff and approval events for this refresh land in the audit JSONL files with change_id `CH-001`.

## Dependencies
- Agents per `docs/AGENTS_RACI.md` remain available for handoffs.
- Interaction stub (`pipelines/interaction_stub.py`) stays unchanged and ready for smoke validation.

## Notes
- Designer will author the detailed task/spec plan based on this brief.
- Implementer and Tester runs must capture their evidence under `artifacts/work/CH-001/run-*/` and `tests/results/CH-001.json`, respectively.
