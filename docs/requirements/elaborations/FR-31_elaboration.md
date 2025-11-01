---
fr_id: FR-31
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#ws-203-implementation-management
  - TRACEABILITY.md#fr-31-partial-change-approvals
status: Draft
---

# 🧩 Requirement Elaboration — FR-31

## 1. Summary
Support partial approvals within a single `CH-###` record by tracking sub-decisions in evaluation docs and change workspaces without branching change IDs.

## 2. Context & Rationale
Complex changes may receive approval for some scope while other tasks require rework. CR002 mandates that partial approvals remain within the original change object, preserving history, audit continuity, and traceability. This requires structured documentation of sub-decisions, remaining tasks, and approval lineage.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `change_workspace` | Markdown (`changes/CH-###/status.md`) | `### Sub-decisions` | Storage location. |
| `impact_report` | Markdown (`docs/IMPACT_REPORT.md`) | Sections referencing partial approvals | Context for scope. |
| `approval_events` | JSONL (`artifacts/phase1/approvals/events.jsonl`) | Stage-specific decisions | Source for sub-decision entries. |
| `tasks` | Markdown (`changes/CH-###/tasks.md`) | Outstanding tasks | Updated when partial approval issued. |
| `traceability_matrix` | Markdown (`TRACEABILITY.md`) | Rows with partial status | Reflects state. |

### Edge & Error Inputs
- Sub-decision not linked to tasks → IM must map tasks or approval cannot proceed.
- Attempt to branch into new change ID → automation warns and enforces single-record policy unless Governance Officer approves split.
- Conflicting partial approvals (e.g., same scope approved and denied) → escalate to Governance Officer for resolution.

## 4. Process Flow
```mermaid
flowchart TD
  A[Approval event received] --> B[Determine affected scope (FR/WS/Task)]
  B --> C[Update change status with sub-decision entry]
  C --> D[Adjust tasks.md (mark completed / remaining)]
  D --> E[Update IMPACT_REPORT & TRACEABILITY partial statuses]
  E --> F[Notify PM, IM, GO of remaining work]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| Markdown | `changes/CH-###/status.md` with `#### Partial Approvals` table | Stakeholders |
| Markdown | `docs/IMPACT_REPORT.md` updated scope | Governance Officer |
| JSON | `artifacts/phase3/partial_approvals/CH-###.json` | Automation |
| JSONL | `audit/approvals.jsonl` enriched entries | Audit |

## 6. Mockups / UI Views (if applicable)
- `artifacts/phase3/screenshots/partial_approval_table.md` — Layout of sub-decisions.
- `artifacts/phase3/screenshots/partial_status_cli.md` — CLI summary.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, plus active change.
- `trace_sections`: `TRACEABILITY.md#ws-203-implementation-management`, `TRACEABILITY.md#fr-31-partial-change-approvals`.
- `artifacts`: `changes/CH-###/status.md`, `docs/IMPACT_REPORT.md`, `TRACEABILITY.md`.

## 7. Acceptance Criteria
* [ ] Partial approval entries capture `{sub_id, scope (FR/WS/Task), decision, approver, notes, follow_up}`.
* [ ] Remaining tasks are updated automatically and linked to approval sub-entry.
* [ ] QA policy engine recognises partial approvals and blocks final merge until outstanding sub-decisions resolve.
* [ ] `/status ch-###` highlights partial approvals and outstanding work.

## 8. Dependencies
- FR-21 Implementation Manager for task updates.
- FR-22 Governance Officer approvals, FR-10 multi-gate logic.
- FR-26 traceability updates reflecting partial states.
- WS-203 Implementation Management workstream.

## 9. Risks & Assumptions
- Excessive granularity could clutter change workspace; use sensible sub-decision grouping.
- Human reviewers must understand the difference between partial approval vs denial; provide clear messages.
- Ensure audit logs differentiate partial approvals from final approvals to avoid reporting confusion.

## 9.1 Retention Notes
- Document whether partially approved scope requires retained runs; mark purge decisions once outstanding work completes.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
