# Change Brief — CH-002 (MS-01 Phase 1 Core Loop Refresh)

## Objective
- Re-execute and extend the Phase 1 multi-agent loop (PM → Designer → Implementer → Tester) so evidence aligns with the refreshed Phase 0 baseline delivered in CH-001.
- Deliver new artifacts for key workstreams: WS-101, WS-102, WS-103, WS-104, WS-106, and WS-109.

## Scope
- **WS-101 Multi-Agent Orchestration**: Re-run orchestrator with current repo state, capturing updated logs, approvals, and audit evidence for FR-01/FR-04/FR-06.
- **WS-102 Concern Lifecycle**: Produce an integration run that exercises raise/update/resolve with mirrored Markdown & audit trail (FR-07).
- **WS-103 Human Approval Gates**: Regenerate approval artifacts that show the new Phase 1 sequence obeys human gate rules (FR-10).
- **WS-104 QA Policy Enforcement**: Implement/enforce CLI hook that blocks promotion when QA thresholds fail (FR-11, TC-FR11-002).
- **WS-106 Status Snapshots**: Add status snapshot tooling to expose stage/capacity metrics (FR-13).
- **WS-109 Implementer Micro-Loop & Retention**: Begin enforcing CR002 updates—planner/executor refinements and automated retention (FR-04, FR-27, FR-29).

## Out of Scope
- Phase 2 governance agents (RA/IA/GO) and downstream dashboards.
- Automation of Phase 0 improvements captured in `backlog/retro_followups_ch001.md`.
- Wider metrics program beyond initial snapshot hook.

## Acceptance Criteria
- Reproducible orchestrator run with updated audit logs, approvals, and documentation references.
- Concern lifecycle demo covering raise → update → resolve with artifacts stored under `artifacts/phase1/concerns/`.
- QA enforcement CLI integrated into Validate stage and referenced in `docs/PROJECT_DETAIL.md`.
- Status snapshot command/tool generates deterministic output for the MS-01 flow.
- Implementer retention script logs auto-purge actions and respects manual retain markers.
- All changes mapped in `TRACEABILITY.md` and summarized for stakeholders.

## Dependencies
- Phase 0 refresh (CH-001) completed and closed.
- Existing orchestrator + concern tooling under `pipelines/` as starting point.
- Human PM availability for stage approvals.

## Notes
- Target seed: `MS01-P1-2025-11-XX` (to be finalized during Spec).
- Coordinated run should produce demo collateral under `artifacts/phase1/orchestration/` for MS-01 sign-off.
