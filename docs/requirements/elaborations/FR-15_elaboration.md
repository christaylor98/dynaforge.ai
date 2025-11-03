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
Deploy a Requirements Analyst (RA) agent that continuously monitors requirement deltas, authoritatively updates traceability artifacts, ingests discovery manifests/System Model Graph projections, and flags downstream ripple effects whenever a `CH-###` modifies functional scope.

## 2. Context & Rationale
CR002 formalises change-centric governance; CR003 adds discovery-first understanding. To keep documentation and workstreams synchronized, the RA agent must observe diffs across `docs/REQUIREMENTS.md`, elaborations, change workspaces, and discovery artifacts, ensuring traceability stays current, discovery coverage status remains accurate, and new workstreams are only spawned with approved elaborations (FR-37). Without automated analysis, manual drift would overwhelm Governance Officer reviews and obscure whether understanding prerequisites are met.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `requirements_snapshot` | Markdown (`docs/REQUIREMENTS.md`) | `### FR-15` section | Baseline for comparison. |
| `elaboration_status` | YAML header (`docs/requirements/elaborations/*.md`) | `status: Approved` | Determines readiness. |
| `change_workspace` | Markdown (`changes/CH-###/spec.md`) | `### Impacted FRs` | Identifies new or altered scope. |
| `traceability_matrix` | Markdown (`TRACEABILITY.md`) | `## Overview by Requirement` | RA updates relevant rows. |
| `system_model_graph` | YAML (`analysis/system_model/components.yaml`, `analysis/system_model/relationships.yaml`) | Graph nodes | Provides canonical understanding context for dependency resolution. |
| `discovery_manifests` | YAML/MD (`analysis/system_manifest.yaml`, `analysis/change_zones.md`, `analysis/intent_map.md`) | Discovery outputs | Used to validate coverage and suggest focus zones. |
| `df_clarify_output` | JSON (`artifacts/analyze/df.clarify.json`) | `{"unlinked_reqs":["FR-15"]}` | Highlights gaps discovered by automation. |

### Edge & Error Inputs
- Elaboration missing or not approved → RA blocks change progression, raises FR-07 concern, and annotates change workspace.
- Snapshot parsing failure → RA logs structured error, falls back to manual review, and re-queues job.
- Requirements delta touches retired FR → RA escalates to PM to confirm reactivation vs archival.

## 4. Process Flow
```mermaid
flowchart TD
  A[Watch requirements + change workspaces] --> B[Detect delta & identify affected FRs]
  B --> C[Verify elaboration status + approvals + discovery coverage]
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
| Markdown | `TRACEABILITY.md` updates linking `FR-###` ↔ `CH-###` and embedding manifest hashes/coverage notes | QA Auditor |
| JSON | `artifacts/phase2/ra/summary.json` with delta metadata | Change Router |
| JSONL | `audit/requirements_analyst.jsonl` event | Audit trail |

## 6. Mockups / UI Views (if applicable)
- `artifacts/mockups/FR-15/ra_delta_report.md` — Report snippet.
- `artifacts/mockups/FR-15/traceability_patch.md` — Example diff RA proposes.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, plus every `CH-###` monitored.
- `trace_sections`: `TRACEABILITY.md#ws-201-requirements-intelligence`, `TRACEABILITY.md#fr-15-requirements-analyst-agent`.
- `artifacts`: `docs/REQUIREMENTS.md`, `TRACEABILITY.md`, `changes/CH-###/status.md`, RA-generated reports.

## 7. Acceptance Criteria
* [ ] RA report lists `{fr_id, ch_id, elaboration_status, discovery_status, impacted_ws, impacted_tc}` for each detected delta.
* [ ] Traceability matrix updates occur within one orchestration cycle of a change entering `Analyzed`.
* [ ] Missing elaborations, stale discovery manifests, or unreviewed System Model Graph nodes automatically issue FR-07 concerns with named owners.
* [ ] `/df.clarify` registers zero unlinked requirements after RA runs, or the RA report documents actionable remediation steps (including discovery refresh recommendations).

## 8. Dependencies
- FR-26 bidirectional traceability enforcement, FR-38 discovery pipeline, FR-39 System Model Graph, FR-41 understanding metrics.
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
