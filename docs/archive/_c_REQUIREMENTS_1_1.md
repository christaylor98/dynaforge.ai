# CR001 1.1 Combined Requirement Updates

## Context
- Change sequence `CR001 → CR001.1 → CR001.2 → CR001.3` introduces an expanded multi-agent governance loop, change-evaluation workflow, and maturity-adaptive process controls.
- Clarification responses captured in the individual impact documents have been consolidated below; remaining gaps appear in the **Open Decisions** section.
- This document supersedes earlier impact notes and should be treated as the single reference when updating `docs/REQUIREMENTS.md`, traceability assets, and agent prompts.

## Updated Functional Requirements
| Requirement ID | Consolidated Update | Key Artifacts / Owners | Source CRs |
| --- | --- | --- | --- |
| FR-01 Project Manager | - Orchestrate RA→IA→IM→QA→TQA→GO loop and coordinate Change Evaluator outcomes.<br>- Detect `maturity_level` from project metadata and activate only the agents required for that level.<br>- Maintain change metrics, maturity state, and ensure Governance Officer reports are consumed before approvals. | `agents/project_manager.py` (PM agent), `PROJECT_METADATA.md`, change dashboards. | 001, 001.1, 001.2, 001.3 |
| FR-02 Status Documentation | - Embed per-change and maturity summaries in `PROJECT_OVERVIEW.md` / `PROJECT_DETAIL.md`.<br>- Cross-link to `CHANGELOG.md`, `IM_PROGRESS.md`, `GOVERNANCE_REPORT.md`, and maturity upgrade records. | PM agent, Governance Officer. | 001.1, 001.2, 001.3 |
| FR-05 Tester-Owned QA Artifacts | - Treat Test Quality Assessor as a standalone agent supplying risk-tier depth metrics.<br>- Incorporate risk-based coverage ratios, maturity band indicators, and Test Quality Summary tables in QA docs. | Tester agent, TQA agent, `tests/TEST_PLAN.md`. | 001, 001.1, 001.3 |
| FR-06 Structured Handoffs | - Extend audit entries with `{fr_id, ws_id, tc_id, raci_role, change_id, maturity_level, artifact_hash}`.<br>- Record maturity upgrades as `CH-###` entries and include evidence paths. | Audit logger, Governance Officer. | 001, 001.2, 001.3 |
| FR-10 Human Approval Gates | - Enforce multi-gate approvals: Impact Assessor → Change Evaluator (advisory) → Governance Officer → PM → Human Reviewer.<br>- Require Governance Officer sign-off from maturity level M2 upward and document satisfied criteria. | PM agent, Governance Officer, Human Reviewer. | 001.1, 001.2, 001.3 |
| FR-11 QA Policy Engine | - Consume risk tiers, Change Evaluator recommendations, and maturity-specific thresholds before merges.<br>- Support partial approvals and ensure QA blocks promotions when unresolved impact deltas exist. | QA policy engine, Change Evaluator. | 001, 001.2, 001.3 |
| FR-13 Status Snapshots | - Report change density, change-to-delivery lag, vision drift indicators, stability ratio, and maturity level/time-in-level in status outputs.<br>- Surface metrics in both Markdown snapshots and CLI dashboards. | PM agent, analytics tooling. | 001, 001.2, 001.3 |

## New Functional Requirements
| Proposed ID | Requirement Summary | Owner | Notes & Clarifications |
| --- | --- | --- | --- |
| FR-15 | Deploy Requirements Analyst agent to monitor requirement deltas, update traceability, and flag ripple risks. | Requirements Analyst | Numbering/ownership confirmed. |
| FR-16 | Stand up Impact Assessor agent to quantify downstream effects, maintain `IMPACT_REPORT.md`, and annotate WS/FR notes. | Impact Assessor | ROI guidance feeds Change Evaluator. |
| FR-17 | Introduce QA Auditor agent to generate traceability gap reports, enforce risk-tier annotations, and update requirement statuses. | QA Auditor | Produces `TRACE_AUDIT.md` and gap sections. |
| FR-18 | Provide Test Synthesizer agent for generating/updating `TC-*` artifacts tied to Impact/QA outputs. | Test Synthesizer | Integrates with QA Auditor and TQA loops. |
| FR-19 | Establish Test Quality Assessor capability to deliver risk-based depth metrics and populate Test Quality Summary tables. | TQA agent | Confirmed as standalone agent. |
| FR-20 | Maintain advisory AI RACI matrix and embed `raci_role` metadata into audit logs and artifacts. | PM / Governance Officer | Backed by RACI matrix from CR001.1. |
| FR-21 | Add Implementation Manager agent to decompose objectives into `WS-*`, track evidence, and publish `IM_PROGRESS.md`. | Implementation Manager | Coordinates with PM and Governance Officer. |
| FR-22 | Add Governance Officer agent to oversee QA/TQA, run compliance checks, and publish `GOVERNANCE_REPORT.md`. | Governance Officer | Signs off maturity upgrades and approvals. |
| FR-23 | Implement automated RA→IA→IM→QA→TQA→GO→PM orchestration triggered on requirement/doc changes. | PM / Implementation Manager | Change Router recommended; may leverage CI hooks. |
| FR-24 | Extend interaction CLI with `/impact` and `/trace` commands supporting both offline and remote/Discord contexts. | Interaction Stub owner | Should work locally and with integrations. |
| FR-25 | Create structured change objects (`CH-###`) captured in `CHANGELOG.md` with affected FR/WS/TC and decision history. | PM / Governance Officer | Supports per-change maturity/log updates. |
| FR-26 | Extend audit schema and CLI endpoints to manage change objects (`/impact`, `/change`, `/approve`). | Governance Officer / Interaction Stub owner | Commands must operate offline and via integrations. |
| FR-27 | Deploy Change Router watcher to trigger orchestration loop when diffs detected. | Implementation Manager | Start with CI-based watcher to reduce ops overhead. |
| FR-28 | Introduce Change Evaluator agent to produce ROI/risk recommendations with human-overridable decisions. | Change Evaluator | AI recommends thresholds; human makes final call. |
| FR-29 | Add Vision Validator agent to score alignment with `VISION.md`/`ARCHITECTURE.md`, feeding advisory signals into Change Evaluator reports. | Vision Validator | Advisory only; no automatic blocking. |
| FR-30 | Implement change velocity dashboard with weekly/milestone metrics accessible via CLI and dashboards. | PM / Analytics owner | Weekly cadence prioritized. |
| FR-31 | Support partial change approvals within a single change record (`CH-###`) with sub-decisions tracked in evaluation docs. | Implementation Manager | No separate IDs needed for partials. |
| FR-32 | Maintain `PROJECT_METADATA.md` (or `project.yaml`) capturing maturity level, last review, criteria, and next target level. | PM / Governance Officer | Acts as single source for maturity-aware agents. |
| FR-33 | Publish `docs/PROCESS_MATURITY_GUIDE.md` describing maturity expectations and agent participation per level. | Governance Officer | Provided in CR001.3; keep synchronized with metadata. |
| FR-34 | Run maturity gate reviews, logging upgrade recommendations and outcomes as `CH-###` entries. | Governance Officer | Triggered per milestone or on demand. |
| FR-35 | Enable maturity-aware prompts/behavior for PM, GO, CE, IM, QA/TQA, and related agents. | Platform / Agent Owners | High effort: shared libraries + regression tests required. |
| FR-36 | Track maturity metrics (time-in-level, upgrade count, active criteria) and surface in `PROJECT_OVERVIEW.md` & CLI `/status`. | PM / Analytics owner | Permanent record plus quick CLI access. |
| FR-37 | Produce approved requirement elaboration files (`docs/requirements/elaborations/FR-###_elaboration.md`) before implementation; leverage RE agent workflow with HR/GO approval gates. | Requirement Elaboration Agent (RE) / Governance Officer | Requirement Elaboration Guide; Elaboration lifecycle and automation hooks. |

## Traceability, Change, and Maturity Artifacts
- `TRACEABILITY.md` must gain risk classifications, `### Unmapped Elements`, `### Test Quality Summary`, `### Artifact Integrity`, and metrics footer sections.
- `CHANGELOG.md` records every change object, including maturity upgrades and partial approvals.
- `IMPACT_REPORT.md`, `IM_PROGRESS.md`, and `GOVERNANCE_REPORT.md` capture change impact, task execution, and compliance evidence respectively.
- Requirement elaborations live under `docs/requirements/elaborations/` and must be approved (per FR-37) before Implementation Manager decomposes workstreams.
- `PROJECT_METADATA.md` stores maturity level, last review date, readiness criteria, and next target level; agents read this to adjust enforcement.
- Audit logs (`audit/*.jsonl`) append `change_id`, `maturity_level`, and content hashes for reproducibility.

## Decision Log & Clarifications
- **Change Evaluator Thresholds:** AI provides ROI/value vs disruption recommendations; human reviewers make the final decision (ROI ≥ 1.5 suggested but not mandatory).
- **Partial Approvals:** Track sub-decisions inside a single `CH-###` record instead of branching IDs.
- **Vision Validator Role:** Advisory only; feeds change evaluation without auto-blocking.
- **CLI Commands:** `/impact`, `/change`, `/trace`, `/approve` should operate both offline and via remote integrations (Discord).
- **Maturity Reviews:** Conduct per milestone (or on human request/change); Governance Officer leads reviews with fallback automation on downgrade.
- **Downgrades:** Supported; agents revert to lighter processes automatically but past work is not reprocessed.
- **Maturity Metrics Visibility:** Must appear in `PROJECT_OVERVIEW.md` and CLI `/status` for rapid checks.
- **Requirement Elaborations:** Implementation Manager must not create `WS-*` entries for an FR until its elaboration file is marked Approved by HR and GO.

Outstanding items inherited from CR001:
- Define canonical templates for `CHANGE_LOG.md`, `IMPACT_REPORT.md`, and Traceability Gap summaries.
- Map risk tiers to QA policy thresholds (e.g., coverage expectations per Critical/High/Medium/Low); to be formalized during implementation.

## Metadata File Strategy (Requested Analysis)
| Approach | Pros | Cons |
| --- | --- | --- |
| **Single repo-level `PROJECT_METADATA.md`** | Simple to maintain; single truth for agents and dashboards; easiest to cache in prompts. | Mixed phases/projects share maturity state; needs additional fields to distinguish concurrent efforts. |
| **Per project/phase metadata file (e.g., `projects/<id>/metadata.yaml`)** | Enables parallel initiatives with independent maturity levels; supports historical snapshots by phase. | Higher coordination overhead; agents must resolve active project scope; risk of drift if files diverge. |

**Recommendation:** Adopt a **single repo-level `PROJECT_METADATA.md`** containing an array of active projects/phases. This keeps agents aligned while allowing per-phase entries, for example:
```yaml
projects:
  - name: "codexa.ai"
    phase: phase-1
    maturity_level: M2
    last_review: 2025-10-30
    next_target_level: M3
    criteria:
      value_proven: true
      governance_enabled: true
  - name: "codexa.ai"
    phase: phase-0
    maturity_level: Archived
```
Agents read the entry matching the active phase (declared in their prompts or task context) and fall back to default rules if no match is found.

## Next Actions
1. Update `docs/REQUIREMENTS.md` to incorporate the revised FR statements and the new FR-15–FR-36 items.
2. Establish initial versions of `CHANGELOG.md`, `IMPACT_REPORT.md`, `IM_PROGRESS.md`, `GOVERNANCE_REPORT.md`, and `PROJECT_METADATA.md`.
3. Plan the rollout for maturity-aware agent prompts (starting with Governance Officer and QA Auditor as suggested).
