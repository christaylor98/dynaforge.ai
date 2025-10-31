# CR001.1 Requirement Impact

## Context
- Change request `docs/CHANGE_REQUEST_001.1.md` supersedes CR001 with an expanded multi-agent governance pattern, introducing the Implementation Manager and Governance Officer roles alongside the previously proposed RA/IA/QA/TQA/TS agents.
- Scope impacts existing functional requirements, adds new agent capabilities, and mandates additional artifacts (e.g., `IM_PROGRESS.md`, `GOVERNANCE_REPORT.md`, enhanced traceability metrics, and a formal RACI matrix).

## Updated Requirements
| Requirement ID | Current Focus | Required Update from CR001.1 | CR001.1 Source |
| --- | --- | --- | --- |
| FR-01 | Project Manager agent maintains requirements and coordinates workflows. | Narrow PM scope to strategic coordination/approvals, delegate task decomposition to the Implementation Manager, and require ingestion of Governance Officer reports before phase closure. | Three-Layer Governance Model → Project Manager; Updated Mermaid Workflow. |
| FR-02 | PM-authored status docs (`PROJECT_OVERVIEW.md`, `PROJECT_DETAIL.md`). | Integrate Implementation Manager progress data and Governance Officer compliance summaries; cross-link to `IM_PROGRESS.md` / `GOVERNANCE_REPORT.md`. | Implementation Manager → Outputs; Governance Officer → Outputs. |
| FR-05 | Tester agent owns QA documentation. | Collaborate with Test Quality Assessor outputs to incorporate risk-tier depth metrics in QA docs and traceability updates. | Extended Agent Ecosystem → TQA; Test Quality Summary recommendation. |
| FR-06 | Structured JSON handoffs with origin/destination metadata. | Append `{fr_id, ws_id, tc_id, raci_role}` and artifact hash/timestamp, aligning with governance and RACI audit needs. | RACI metadata in audit logs; Evidence Integrity upgrades. |
| FR-10 | Enforce human approval for plan changes and promotions. | Require Governance Officer sign-off before HR approval and embed advisory RACI markers in approval evidence. | Three-Layer Governance Model → Governance Officer; RACI Matrix guidance. |
| FR-11 | QA policy engine gates merges based on QA results. | Consume Governance Officer / TQA findings (risk coverage, outstanding impact deltas) and block promotions until governance gate passes. | Extended Agent Ecosystem → QA/TQA; Governance Officer responsibilities. |
| FR-13 | Regular status snapshots with metrics. | Expand snapshots to include risk-class coverage, traceability gap counts, and governance status for HR visibility. | Traceability Additions → Metrics Summary; Governance Officer outputs. |

## New Requirements
| Proposed ID | Requirement Summary | Primary Owner | Motivation from CR001.1 |
| --- | --- | --- | --- |
| FR-15 (proposed) | Deploy a Requirements Analyst agent to monitor requirement deltas, update traceability, and raise impact summaries. | Requirements Analyst | Recommended Agent Roles → RA; Workflow Loop diagram. |
| FR-16 (proposed) | Provide an Impact Assessor agent that quantifies downstream effects, updates WS/FR notes, and publishes `IMPACT_REPORT.md` / `artifacts/impact_deltas.json`. | Impact Assessor | Recommended Agent Roles → IA; Implementation Strategy Phase A–C. |
| FR-17 (proposed) | Establish a QA Auditor agent to validate FR↔WS↔Test linkage, generate Traceability Gap reports, and update statuses with risk tiers. | QA Auditor | Recommended Agent Roles → QA; Traceability Gaps recommendation. |
| FR-18 (proposed) | Add a Test Synthesizer agent to generate/update `TC-*` tests aligned with IA/QA findings and maintain traceability links. | Test Synthesizer | Recommended Agent Roles → TS; Workflow Loop diagram. |
| FR-19 (proposed) | Create a Test Quality Assessor capability that produces risk-tier coverage metrics (Required Depth vs Actual Cases) for QA gating. | Test Quality Assessor | Suggested Additions → Test Quality Summary; Extended Agent Ecosystem. |
| FR-20 (proposed) | Maintain an advisory AI RACI matrix artifact and embed RACI metadata into audit logs for explainability. | Project Manager / Governance Officer | RACI Matrix section; Runtime guidance. |
| FR-21 (proposed) | Introduce an Implementation Manager agent to decompose PM objectives into `WS-*` tasks, track execution evidence, and publish `docs/IM_PROGRESS.md`. | Implementation Manager | Three-Layer Governance Model → Implementation Manager; Outputs table. |
| FR-22 (proposed) | Stand up a Governance Officer agent to oversee QA/TQA outputs, ensure audit completeness, and publish `docs/GOVERNANCE_REPORT.md` before approvals. | Governance Officer | Three-Layer Governance Model → Governance Officer; Governance layer benefits. |
| FR-23 (proposed) | Add orchestration rules that ensure the RA→IA→IM→QA→TQA→GO→PM loop executes automatically on requirement changes (watchers on `requirements/` & `docs/`). | Project Manager / Implementation Manager | Recommended Workflow Loop; Implementation Strategy Phase C. |
| FR-24 (proposed) | Expose `/impact` and `/trace` CLI commands in the interaction stub for on-demand impact and traceability reports. | Interaction Stub owner | Implementation Strategy Phase E; CLI extension recommendation. |

## Traceability, Audit, and Artifact Updates
- **Risk Classification & Depth:** Extend `TRACEABILITY.md` tables with `Risk` and required depth metadata; ensure QA/TQA populate coverage ratios in the `### Test Quality Summary`.
- **Unmapped Elements Report:** Generate `### Unmapped Elements` sections enumerating unlinked FRs, orphan tests, and stale WS entries, owned by the QA Auditor.
- **Artifact Integrity Ledger:** Record artifact path, hash, and timestamp in each traceability refresh to satisfy Governance Officer evidence checks.
- **Change & Impact Logs:** Produce `CHANGE_LOG.md` and `IMPACT_REPORT.md` as part of the Implementation Strategy (Phase A) for longitudinal requirement tracking.
- **RACI & Governance Artifacts:** Maintain `docs/RACI_MATRIX.md`, `docs/IM_PROGRESS.md`, and `docs/GOVERNANCE_REPORT.md`, linking them in PM status docs and audit trails.
- **Mermaid Workflow Update:** Replace existing orchestration diagrams with the PM↔IM↔GO flow to keep documentation aligned with the new governance hierarchy.

## Follow-ups / Questions
- Confirm numbering/ownership for FR-15 through FR-24 before updating `docs/REQUIREMENTS.md` and other baseline documents.
Confirmed
- Decide whether the Test Quality Assessor is a dedicated agent or a role folded into existing Tester/QA agents for implementation planning.
Dedicated agent
- Align on templates for `IM_PROGRESS.md`, `GOVERNANCE_REPORT.md`, `CHANGE_LOG.md`, and `IMPACT_REPORT.md` to keep outputs consistent across agents.
Will assess during implementation
- Determine how governance sign-off integrates with existing approval markers and whether new inline annotations are needed for GO and HR approvals.
Process will be assessed and refined during implementation
