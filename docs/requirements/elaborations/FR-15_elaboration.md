---
fr_id: FR-15
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#ws-201-requirements-intelligence
  - TRACEABILITY.md#fr-15-requirements-analyst-agent
status: Draft
---

# 🧩 Requirement Elaboration — FR-15

## 1. Summary
Deploy a Requirements Analyst (RA) agent that continuously monitors requirement deltas, authoritatively updates traceability artifacts, and flags downstream ripple effects whenever a `CH-###` modifies functional scope.

## 2. Context & Rationale
CR002 formalises change-centric governance. To keep documentation and workstreams synchronized, the RA agent must observe diffs across `docs/REQUIREMENTS.md`, elaborations, and change workspaces, ensuring traceability stays current and new workstreams are only spawned with approved elaborations (FR-37). Without automated analysis, manual drift would overwhelm Governance Officer reviews.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `requirements_snapshot` | Markdown (`docs/REQUIREMENTS.md`) | `### FR-15` section | Baseline for comparison. |
| `elaboration_status` | YAML header (`docs/requirements/elaborations/*.md`) | `status: Approved` | Determines readiness. |
| `change_workspace` | Markdown (`changes/CH-###/spec.md`) | `### Impacted FRs` | Identifies new or altered scope. |
| `traceability_matrix` | Markdown (`TRACEABILITY.md`) | `## Overview by Requirement` | RA updates relevant rows. |
| `df_clarify_output` | JSON (`artifacts/analyze/df.clarify.json`) | `{"unlinked_reqs":["FR-15"]}` | Highlights gaps discovered by automation. |

### Edge & Error Inputs
- Elaboration missing or not approved → RA blocks change progression, raises FR-07 concern, and annotates change workspace.
- Snapshot parsing failure → RA logs structured error, falls back to manual review, and re-queues job.
- Requirements delta touches retired FR → RA escalates to PM to confirm reactivation vs archival.

## 4. Process Flow
```mermaid
flowchart TD
  A[Watch requirements + change workspaces] --> B[Detect delta & identify affected FRs]
  B --> C[Verify elaboration status + approvals]
  C --> D[Update traceability entries + link CH-###]
  D --> E[Generate ripple analysis (related WS/TC)]
  E --> F[Publish RA report + notify PM/GO]
  F --> G{Gaps remain?}
  G -->|Yes| H[Raise concern + assign owner]
  G -->|No| I[Mark analysis complete in change workspace]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| Markdown | `docs/requirements/intel/FR-15_report.md` | PM, Governance Officer |
| Markdown | `TRACEABILITY.md` updates linking `FR-###` ↔ `CH-###` | QA Auditor |
| JSON | `artifacts/phase2/ra/summary.json` with delta metadata | Change Router |
| JSONL | `audit/requirements_analyst.jsonl` event | Audit trail |

## 6. Mockups / UI Views (if applicable)
- `artifacts/phase2/screenshots/ra_delta_report.md` — Report snippet.
- `artifacts/phase2/screenshots/traceability_patch.md` — Example diff RA proposes.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, plus every `CH-###` monitored.
- `trace_sections`: `TRACEABILITY.md#ws-201-requirements-intelligence`, `TRACEABILITY.md#fr-15-requirements-analyst-agent`.
- `artifacts`: `docs/REQUIREMENTS.md`, `TRACEABILITY.md`, `changes/CH-###/status.md`, RA-generated reports.

## 7. Acceptance Criteria
* [ ] RA report lists `{fr_id, ch_id, elaboration_status, impacted_ws, impacted_tc}` for each detected delta.
* [ ] Traceability matrix updates occur within one orchestration cycle of a change entering `Analyzed`.
* [ ] Missing elaborations or approvals automatically issue FR-07 concerns with named owners.
* [ ] `/df.clarify` registers zero unlinked requirements after RA runs, or the RA report documents actionable remediation steps.

## 8. Dependencies
- FR-26 bidirectional traceability enforcement.
- FR-37 elaboration workflow status.
- FR-23 automated orchestration triggers to invoke RA tasks.
- WS-201 Requirements Intelligence workstream.

## 9. Risks & Assumptions
- Over-aggressive diff detection may create noise; implement ignore patterns for cosmetic changes.
- Large documentation rewrites could overwhelm summary generation; RA should chunk updates and request human oversight.
- Requires consistent YAML headers in elaborations; missing metadata must fail fast.

## 9.1 Retention Notes
- RA evidence is lightweight; retention primarily references Implementer runs when gaps originate from failed execution. Document retained run IDs when RA blocks promotion pending review.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
