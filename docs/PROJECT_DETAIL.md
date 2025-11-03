# Project Detail

## Scope & Boundaries
MS-02 focuses on the discovery-first workflow: context intake → discovery run → iteration follow-ups → requirement curation → loop planning → seed packaging → conversational approvals → governance publication → MS-01 execution rail handoff.

## Deliverables
- Discovery configuration + telemetry (`docs/discovery/config.yaml`, `docs/status/iteration_log.md`) with follow-up tracking.
- Loop plan artifacts (`loop-plan.json`) capturing human-selected execution scope (requirement/change/phase/milestone).
- Seed bundles generated via `codexa seed --from loop-plan` with review digests in `changes/CH-###/seed/REVIEW.md`.
- Governance summaries (`artifacts/ms02/storyboard/summary.md`, `gaps.md`) demonstrating prompt-first approvals and readiness reporting.
- Updated documentation & traceability (`TRACEABILITY.md`, `docs/ARCHITECTURE.md`, `docs/TECH_STACK.md`, `docs/AGENTS_RACI.md`, `docs/REQUIREMENTS_1_3.md`) reflecting the storyboard.

## Implementation Notes
- Scenario: MS-02 Discovery MVP (changes `CH-010+`).
- Requirements emphasis: FR-38 (discovery pipeline), FR-39 (System Model Graph projections), FR-40 (loop plan → seed packaging), FR-41 (understanding metrics).
- Primary actions executed / expected:
  - `codexa discover --config docs/discovery/config.yaml` (full mode by default; quick mode on request).
  - Conversational follow-up handling (`accept follow-up issue-12`, etc.) updating `docs/status/iteration_log.md`.
  - `codexa loop plan --change CH-010` (or requirement/phase/milestone) capturing scope.
  - `codexa seed --from loop-plan --tests pytest` producing scoped bundle under `changes/CH-010/seed/`.
  - AI-driven review conversation culminating in `codexa approve scope --from loop-plan` or logged waivers.
  - Governance summary prompt (“Ready to publish?”) producing `summary.md` + `gaps.md` ahead of `codexa loop start --from loop-plan`.
  - `python3 scripts/ms02_dry_run.py` to regenerate sample artifacts for demos or onboarding.
- Evidence points: discovery manifests (`analysis/`), System Model Graph projections (`analysis/system_model/`), iteration log entries, loop-plan JSON revisions, review digest history, governance summaries, and updated traceability references.

<!-- concerns:start -->

### Concern Summary

#### Open Concerns

- None at this time.

#### Resolved Concerns

| ID | Severity | Message | Raised By | Raised At | Resolution | Resolved At |
| -- | -------- | ------- | --------- | --------- | ---------- | ----------- |
| 6fe0ebf4e6f74ed1bc740f974a2f55d9 | medium | Sample concern for WS-102 validation. | tester | 2025-10-29T10:57:14.899Z | Patched in latest build. | 2025-10-29T10:58:29.409Z |
| CH2-CONC-001 | medium | Integration demo failure path | tester | 2025-11-02T04:10:07.825Z | Integration pass confirmed | 2025-11-02T04:10:21.090Z |

<!-- concerns:end -->

## Review Checklist
- Discovery telemetry logged (`docs/status/iteration_log.md`, `analysis/system_manifest.yaml` metadata).
- Loop plan captured and stored (`loop-plan.json`).
- Seed bundle and review digest ready (`changes/CH-010/seed/…`, `REVIEW.md`).
- Governance summary published (or pending with `gaps.md`).
- Approvals/waivers recorded in traceability and audit logs.

## Appendix
- Storyboard: `design/MS-02_storyboard.md`
- Iteration log: `docs/status/iteration_log.md`
- Governance summary: `artifacts/ms02/storyboard/summary.md`

_Updated for MS-02 discovery milestone alignment at 2025-11-04 15:30:00Z._
