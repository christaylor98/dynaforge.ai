---
fr_id: FR-10
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#fr-10-approval-governance
  - TRACEABILITY.md#ws-204-governance--multi-gate-approvals
status: Draft
---

# 🧩 Requirement Elaboration — FR-10

## 1. Summary
Enforce multi-gate approvals (Impact Assessor → Change Evaluator (advisory) → Governance Officer → Project Manager → Human Reviewer) so every `CH-###` pauses for validation, records decision paths, and syncs lifecycle states before progression.

## 2. Context & Rationale
Governance is a core selling point of Dynaforge. FR-10 guarantees the staged approval ladder runs in the correct order for each maturity level, with the PM respecting decisions, updating `changes/CH-###/status.md`, and logging them for audit. CR002 introduces Governance Officer participation, advisory Change Evaluator signals, and retention coordination so denials trigger FR-07 concerns and rework loops instead of silent failures.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `approval_request` | JSON (`artifacts/phase1/approvals/pending.json`) | `{"fr_id":"FR-10","ch_id":"CH-017","stage":"Governance Officer","state":"Awaiting Decision"}` | Created when PM pauses for review. |
| `command_event` | Dict from FR-08 | `{"cmd":"/approve","user":"@governance","note":"Compliance satisfied","ch_id":"CH-017"}` | Human/agent action.
| `raci_matrix` | Markdown (`docs/AGENTS_RACI.md`) | `Governance Officer: Approver`, `Impact Assessor: Advisor` | Confirms permissions.
| `maturity_policy` | YAML (`PROJECT_METADATA.md`) | `M2: ["Impact Assessor","Change Evaluator","Governance Officer","PM","HR"]` | Defines gate order per maturity.
| `df_checklist_output` | JSON (`artifacts/analyze/df_checklist.json`) | `{"ch_id":"CH-017","status":"pass"}` | Required before Governance Officer approval.
| `retention_summary` | JSON (`artifacts/work/CH-017/run-*/summary.json`) | `{"retained":true,"reason":"awaiting GO review"}` | Provides context for approvals.

### Edge & Error Inputs
- Unauthorized user attempts approval → system denies, logs attempt with severity `warning`, keeps request pending, and notifies Governance Officer.
- Timeout (no response within SLA) → escalate via `/status blockers`, notify PM, and keep loop paused; after threshold, raise FR-07 concern.
- Denial with remediation note → create follow-up task in `changes/CH-###/tasks.md`, mark change `Rework Needed`, and block auto-resume until addressed.
- Advisor (Change Evaluator) recommends rejection → log advisory decision but allow final approvers to override with recorded rationale.

## 4. Process Flow
```mermaid
flowchart TD
  A[PM submits approval_request] --> B[Determine gate order from maturity + RACI]
  B --> C[Notify advisor stages (Impact Assessor, Change Evaluator)]
  C --> D[Collect advisory signals + update request]
  D --> E[Notify Governance Officer]
  E --> F[Await `/approve` or `/deny` with checklist verification]
  F --> G{Decision}
  G -->|Approve| H[Transition change to Partially Approved + notify PM]
  G -->|Deny| I[Record denial, update change to Rework Needed, create tasks]
  H --> J[Notify PM + request HR approval]
  J --> K[HR decision]
  K --> L[Update docs, audit trail, retention status]
  I --> L
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| JSONL | `artifacts/phase1/approvals/events.jsonl` decision log with `{stage, actor, ch_id, fr_id, decision, advisory_refs}` | Governance Officer, QA |
| Markdown | `docs/PROJECT_DETAIL.md` approval badges tied to `CH-###` lifecycle state | Stakeholders |
| Markdown | `changes/CH-###/status.md` updated with staged approval entries | PM, HR |
| Text | CLI/Discord confirmation message with correlation ID and next required gate | Human reviewer

## 6. Mockups / UI Views (if applicable)
- `artifacts/phase1/screenshots/approval_flow_cli.md` — CLI approval sequence showing staged gating.
- `artifacts/phase1/screenshots/approval_badge.md` — Doc badge showing pending/approved with gate list.
- `artifacts/phase1/screenshots/approval_timeline.md` — Visualization of gate order per maturity.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, subsequent `CH-###` entries representing approvals.
- `trace_sections`: `TRACEABILITY.md#fr-10-approval-governance`, `TRACEABILITY.md#ws-204-governance--multi-gate-approvals`.
- `artifacts`: `artifacts/phase1/approvals/events.jsonl`, `changes/CH-###/status.md`, `docs/PROJECT_DETAIL.md`.

## 7. Acceptance Criteria
* [ ] Every change lifecycle transition to `Partially Approved`/`Approved` records staged approvals in the mandated order for the current maturity.
* [ ] Approval events include `{fr_id, ws_id, ch_id, stage, reviewer_handle, decision, note, advisory_refs[], checklist_hash}`.
* [ ] Denials trigger PM to reopen the RA→IA→IM→QA loop, append tasks to `changes/CH-###/tasks.md`, and log FR-07 concern.
* [ ] Audit log, `changes/CH-###/status.md`, and documentation stay in sync within one orchestration cycle; `/status ch-###` reflects current stage.

## 8. Dependencies
- FR-08 commands (`/approve`, `/deny`), FR-09 routing/logging.
- FR-06 logging to persist approval events, FR-26 traceability, FR-28 `/df.checklist`.
- FR-02 documentation to surface badges, FR-11 QA gating for readiness.
- WS-103 human approval gates, WS-204 governance & multi-gate approvals, WS-108 demo documentation.

## 9. Risks & Assumptions
- Assumes reviewer identity can be validated against RACI; ensure environment config maps CLI/Discord handles to roles.
- Gate ordering may expand in future maturities; design allows injecting additional checkpoints via policy file.
- Excessive approvals could slow loop; consider batching advisory reviews but never final approvals.
- Missing `/df.checklist` results must block Governance Officer; integrate strongly with FR-28 outputs.

## 9.1 Retention Notes
- When denials occur, Implementer retains latest run automatically; approval flow records retention rationale and link.
- Upon final approval, retention is reassessed; if cleared, log purge event in approvals file for FR-27 compliance.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
