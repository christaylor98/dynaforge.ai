---
fr_id: FR-16
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#ws-202-impact-assessment--evaluator
  - TRACEABILITY.md#fr-16-impact-assessor-agent
status: Draft
---

# 🧩 Requirement Elaboration — FR-16

## 1. Summary
Stand up an Impact Assessor (IA) agent that quantifies downstream effects of requirement changes, incorporates discovery manifests and System Model Graph insights, maintains `IMPACT_REPORT.md`, and annotates workstream/requirement notes so approvals proceed with clear risk/benefit visibility.

## 2. Context & Rationale
Change objects often touch multiple requirements, tests, and documentation. The IA agent provides structured analysis—scoring ROI, complexity, discovery readiness, and affected artifacts—so the Change Evaluator, Governance Officer, and PM can make informed decisions. CR002 expects this analysis to be serialized per `CH-###` and linked into the approval ladder; CR003 adds discovery-first understanding, requiring IA to confirm sufficient manifest coverage and System Model Graph alignment before recommending progression.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `change_workspace` | Markdown (`changes/CH-###/spec.md`) | `### Impacted Areas` | Source scope for analysis. |
| `requirements_delta` | Markdown diff (`docs/REQUIREMENTS.md`) | `- FR-18 updated` | Highlights changed requirements. |
| `traceability_snapshot` | Markdown (`TRACEABILITY.md`) | `WS-203 row` | Used to locate dependent workstreams. |
| `test_catalog` | Markdown (`tests/TEST_PLAN.md`) | `TC-FR18-*` entries | Identifies affected tests. |
| `historical_metrics` | JSON (`artifacts/metrics/impact_history.json`) | `{"average_duration":480}` | Provides baseline for scoring. |
| `discovery_manifests` | YAML/MD (`analysis/system_manifest.yaml`, `analysis/change_zones.md`, `analysis/intent_map.md`) | `modules: [...]` | Supplies structural context and manifest hashes to assess coverage. |
| `system_model_graph` | YAML (`analysis/system_model/components.yaml`, `analysis/system_model/relationships.yaml`) | `node: fr-18` | Enables dependency traversal for ripple mapping. |
| `understanding_metrics` | YAML (`analysis/metrics/understanding_coverage.yaml`) | `coverage: 0.68` | Provides readiness signal for impacted zones. |

### Edge & Error Inputs
- Missing change scope → IA flags `analysis_pending`, requests PM clarification, and blocks approvals.
- Unable to map FR to workstreams → log gap, raise FR-26 traceability warning, and include manual follow-up.
- ROI calculation fails due to missing metrics → IA defaults to conservative risk rating and highlights missing data in report.

## 4. Process Flow
```mermaid
flowchart TD
  A[Ingest change_workspace + deltas] --> B[Map FRs to workstreams/tests/discovery zones]
  B --> C[Compute impact scores (risk, effort, opportunity, readiness)]
  C --> D[Summarise required follow-up actions]
  D --> E[Update IMPACT_REPORT.md + change status]
  E --> F[Notify Change Evaluator & Governance Officer]
  F --> G[Attach impact digest to approval request]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| Markdown | `docs/IMPACT_REPORT.md` entry for `CH-###` (including discovery readiness + manifest hashes) | Change Evaluator, Governance Officer |
| JSON | `artifacts/phase2/impact/CH-###.json` with scoring | PM, analytics |
| Markdown | `changes/CH-###/impact.md` appended with IA summary | PM, Implementer |
| JSONL | `audit/impact_assessor.jsonl` record | Audit |

## 6. Mockups / UI Views (if applicable)
- `artifacts/mockups/FR-16/impact_scorecard.md` — Sample ROI/risk table.
- `artifacts/mockups/FR-16/impact_dependency_map.md` — Visualization of affected workstreams.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, plus the active `CH-###` under review.
- `trace_sections`: `TRACEABILITY.md#ws-202-impact-assessment--evaluator`, `TRACEABILITY.md#fr-16-impact-assessor-agent`.
- `artifacts`: `docs/IMPACT_REPORT.md`, `changes/CH-###/impact.md`, `artifacts/phase2/impact/`.

## 7. Acceptance Criteria
* [ ] IA report lists `{fr_id, ws_id, tc_id, impact_score, readiness_status, discovery_gaps, recommended_actions}` for each affected component.
* [ ] Change Evaluator receives structured JSON entry ready for ROI computation within the same orchestration cycle.
* [ ] IA highlights missing traceability, stale discovery manifests, or unapproved elaborations and raises FR-07 concerns when blocking issues are detected.
* [ ] `IMPACT_REPORT.md` entries include links to retained Implementer runs when manual verification is required.

## 8. Dependencies
- FR-15 RA outputs for requirement delta detection.
- FR-23 orchestration triggers to invoke IA automatically.
- FR-26 traceability updates, FR-27 retention references, FR-38 discovery pipeline, FR-39 System Model Graph, FR-41 understanding metrics.
- WS-202 Impact Assessment & Evaluator, WS-205 change router.

## 9. Risks & Assumptions
- Impact scoring relies on historical metrics; poor baselines can skew recommendations—provide manual override.
- High volume of simultaneous changes could overwhelm IA; queue analysis per change to prevent contention.
- Requires consistent naming and metadata across requirements, workstreams, and tests; RA and Traceability must remain accurate.

## 9.1 Retention Notes
- When IA recommends manual verification, ensure retained Implementer runs are linked in the report with reason and expected purge date.
- Once change merges, IA records retention outcome (purged or retained for audit) in `artifacts/phase2/impact/CH-###.json`.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
