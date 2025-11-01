---
fr_id: FR-03
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#fr-03-designer-agent-deliverables
status: Draft
---

# 🧩 Requirement Elaboration — FR-03

## 1. Summary
Enable the Designer agent to transform `CH-###` objectives and PM briefs into actionable architecture and design guidance (`ARCHITECTURE.md`, `DESIGN_SPEC.md`) that downstream agents can execute without ambiguity, while documenting change impacts and traceability links required by FR-26.

## 2. Context & Rationale
In the spike, the Designer provides concrete deliverables (`design/ARCHITECTURE.md`, `design/DESIGN_SPEC.md`) that downstream agents can follow without extra context. CR002 adds expectations: design artifacts must reference the originating `CH-###`, enumerate traceability anchors, and highlight maturity-driven constraints (e.g., governance hooks at M2). This ensures Implementer/QA agents honour change scopes and that new specs integrate cleanly into the change workspace.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `change_brief` | Markdown (`changes/CH-###/spec.md`) | `## Summary\nExpand audit schema` | Primary objective and scope. |
| `pm_brief` | Markdown (`docs/IMPLEMENTATION_PLAN.md`) | `### FR-03\n- expand handoff logging schema` | Additional narrative from PM. |
| `concerns` | JSON (`artifacts/phase1/concerns/open.json`) | `{"id":"C-012","topic":"schema drift","ch_id":"CH-017"}` | Influences design decisions. |
| `governance_requirements` | Markdown (`docs/GOVERNANCE_REPORT.md`) | `### Required Controls` | Non-negotiable constraints. |
| `existing_artifacts` | Markdown | `design/ARCHITECTURE.md` prior version | Allows diff-aware updates and retention via `CH-###` references. |

### Edge & Error Inputs
- No open concerns → Designer documents validation (“No active concerns as of YYYY-MM-DD”) to avoid silent omissions.
- Conflicting governance inputs → raise new concern via FR-07 and flag `changes/CH-###/status.md` before publishing.
- Missing prior artifacts → Designer creates baseline files with minimal skeleton, annotates rationale, and informs PM.

## 4. Process Flow
```mermaid
flowchart TD
  A[Receive change_brief + PM context] --> B[Collect concerns & governance needs]
  B --> C[Draft architecture decisions, assumptions, maturity impacts]
  C --> D[Update ARCHITECTURE.md sections with change references]
  C --> E[Update DESIGN_SPEC.md with steps, inputs/outputs, traceability]
  D --> F[Generate review checklist + highlight open questions]
  E --> F
  F --> G[Log handoff (Designer→Implementer) with ch_id + artifact hashes]
  G --> H[Update changes/CH-###/impact.md with design summary]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| Markdown | `design/ARCHITECTURE.md` component diagram + change rationale referencing `CH-###` | Implementer, PM |
| Markdown | `design/DESIGN_SPEC.md` scenario tables with traceability links | Implementer, Tester |
| JSONL | `audit/handoffs.jsonl` Designer→Implementer entry with `{fr_id:"FR-03","ch_id":"CH-###","artifact_hash":"..."}` | Audit trail |
| Markdown | `changes/CH-###/impact.md` updated with design deltas and dependencies | Governance Officer, Impact Assessor |

## 6. Mockups / UI Views (if applicable)
- `artifacts/phase1/mockups/designer_flow.md` — Sequence diagram for MS-01 data path.
- `artifacts/phase1/mockups/designer_tables.md` — Example scenario coverage table referencing `CH-###`.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, additional `CH-###` triggered by new design requirements.
- `trace_sections`: `TRACEABILITY.md#fr-03-designer-agent-deliverables`, `TRACEABILITY.md#ws-101-multi-agent-orchestration`.
- `artifacts`: `design/ARCHITECTURE.md`, `design/DESIGN_SPEC.md`, `changes/CH-###/impact.md`, `TRACEABILITY.md`.

## 7. Acceptance Criteria
* [ ] Design spec includes “Happy Path”, “Edge Cases”, “Governance Considerations”, and “Change Impacts” subsections.
* [ ] All referenced FRs/WSs and `CH-###` IDs link back to traceability matrix entries and change workspace metadata.
* [ ] Designer logs open questions when requirements are ambiguous; Implementer should never receive silent assumptions.
* [ ] Designer handoff includes artifact hashes, `ch_id`, and maturity annotations recorded in audit log.

## 8. Dependencies
- FR-01 orchestration triggers (PM dispatch), FR-26 traceability enforcement.
- FR-07 concern lifecycle for unresolved topics, FR-06 logging schema to include Designer evidence.
- FR-04 Implementer alignment, FR-11 QA gating for validation of design assumptions.
- WS-101 core loop implementation, WS-205 change router, WS-201 requirements intelligence.

## 9. Risks & Assumptions
- Designer relies on up-to-date change briefs; stale `changes/CH-###/spec.md` could misguide design—mitigated by PM review.
- Overly detailed specs might bottleneck progress; maintain “just enough” detail for MS-01 while capturing governance hooks.
- Visual assets must stay under repo size limits; prefer diagrams generated via Mermaid when possible.

## 9.1 Retention Notes
- If design iterations require Implementer to retain run artifacts, Designer must note the rationale and expected retention duration in `changes/CH-###/impact.md`.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
