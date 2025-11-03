---
fr_id: FR-01
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#fr-01-project-manager-agent-coordination
status: Draft
---

# 🧩 Requirement Elaboration — FR-01

## 1. Summary
Enable the Project Manager (PM) agent to orchestrate change-centric workflows that begin with a `CH-###` anchor, dispatch the RA→IA→IM→QA→TQA→GO sequence based on `PROJECT_METADATA.md` maturity settings, and maintain visibility into staged approvals before HR sign-off.

## 2. Context & Rationale
MS-01 demonstrates a closed loop where the PM agent translates stakeholder goals into actionable change objects. CR002 extends this responsibility: every orchestration run must originate from a `CH-###` workspace, consume Governance Officer reports before completion, and surface maturity-aware metrics so humans can judge readiness. FR-01 is the backbone of that demo—without change-centric orchestration the other agents remain disconnected and the human lacks traceability into staged approvals and lifecycle state.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `change_workspace` | Markdown bundle (`changes/CH-###/status.md`) | lifecycle: `In-Progress` | Source of truth for change state and linked FRs. |
| `project_metadata` | YAML (`PROJECT_METADATA.md`) | `maturity_level: M2` | Drives which agents must be engaged before approvals. |
| `governance_report` | Markdown (`docs/GOVERNANCE_REPORT.md`) | Section `### Outstanding Concerns` | Required sign-off before HR approval. |
| `agent_handoff` | JSONL (`audit/handoffs.jsonl`) | `{"from":"PM","to":"ImplementationManager","fr_id":"FR-04","ch_id":"CH-017"}` | Captures handoffs with change and maturity metadata. |
| `human_command` | CLI / Discord command | `/status ch-017` | Injects clarifications, approvals, or denials. |

### Edge & Error Inputs
- Missing `project_metadata` → PM defaults to M0 behaviour and emits FR-07 concern referencing `CH-###`.
- Governance Officer raises non-compliance → PM places change in `Partially Approved`, notifies Implementer for rework, and blocks HR approval.
- Human denies approval (`/deny`) → PM records denial, updates change lifecycle to `Rework Needed`, and awaits new instruction.

## 4. Process Flow
```mermaid
flowchart TD
  A[Receive change_workspace] --> B[Parse metadata + maturity]
  B --> C[Validate staged approvals + GO reports]
  C --> D[Dispatch RA/IA (if required by maturity)]
  D --> E[Dispatch IM with scoped WS tasks]
  E --> F[Log Implementer run + retention policy]
  F --> G[Dispatch QA/TQA and collect outcomes]
  G --> H[Request Governance Officer sign-off]
  H --> I{HR approval received?}
  I -->|Yes| J[Transition change to Approved/Merged + publish status]
  I -->|No| K[Pause, record FR-07 concern, request clarification]
  K --> C
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| Markdown | `docs/PROJECT_OVERVIEW.md` / `docs/PROJECT_DETAIL.md` updated with change lifecycle and maturity metrics | Human stakeholders |
| JSONL | `audit/handoffs.jsonl` entries including `{fr_id, ch_id, maturity_level, raci_role}` | Audit / QA reviewers |
| Markdown | `changes/CH-###/status.md` updated to `Partially Approved` / `Approved` states | Governance Officer, HR |
| Log | `artifacts/phase1/orchestration/run.log` (with run_id, seed) | Observability + FR-27 retention audits |

## 6. Mockups / UI Views (if applicable)
- `artifacts/mockups/FR-01/pm_status_cli.md` — CLI snapshot showing `/status ch-017` with change lifecycle.
- `artifacts/mockups/FR-01/pm_approval_wait.md` — Visual showing paused loop awaiting Governance Officer sign-off.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002` (adopts change-centric governance), future `CH-###` entries per feature.
- `trace_sections`: `TRACEABILITY.md#fr-01-project-manager-agent-coordination`, `TRACEABILITY.md#ws-205-change-router--orchestration`.
- `artifacts`: `docs/REQUIREMENTS_1_2.md`, `CHANGELOG.md`, `changes/CH-###/status.md`, `PROJECT_METADATA.md`.

## 7. Acceptance Criteria
* [ ] PM agent produces ordered RA→IA→IM→QA→TQA→GO dispatches based on maturity settings with deterministic IDs.
* [ ] Handoff log captures `{fr_id, ws_id, ch_id, maturity_level, raci_role}` for every transition.
* [ ] PM blocks progression when Governance Officer or HR approvals are missing, updates change lifecycle to `Partially Approved`, and surfaces prompts via CLI/Discord.
* [ ] `/status ch-###` and `/status milestone` return narratives updated within 60 seconds, including staged approval state and retention summary.

## 8. Dependencies
- FR-02 for publishing documentation snapshots.
- FR-06 for structured handoff logging schema, FR-26 for traceability links.
- FR-10 for multi-gate approval enforcement, FR-11 for QA gating, FR-27 for retention policy coordination.
- WS-101 orchestration runtime, WS-205 change router, WS-109 Implementer micro-loop.

## 9. Risks & Assumptions
- Assumes downstream agents expose deterministic seeds; non-determinism can break audit expectations.
- Missing or stale `PROJECT_METADATA.md` may lead to incorrect gate sequencing; mitigation is default to M0 and raise FR-07 concern.
- Change lifecycle updates must remain atomic; partial writes could desync `changes/CH-###/status.md` and `TRACEABILITY.md`.

## 9.1 Retention Notes
- Implementer runs tagged to this change must purge automatically after 48 h/2 GB unless the PM sets `--retain` for Governance Officer review.
- Retained runs require a comment in `changes/CH-###/status.md` explaining the retention rationale for FR-27 compliance.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
