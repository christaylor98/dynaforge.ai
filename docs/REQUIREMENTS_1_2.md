# CR002 1.2 Combined Requirement Updates

## Context
- Change sequence `CR001 → CR001.1 → CR001.2 → CR001.3 → CR002` establishes a change-centric governance model with multi-agent orchestration, maturity-aware controls, and deterministic Implementer execution.
- This document consolidates `docs/REQUIREMENTS_1_1.md` and `docs/change_ideas_002.md` so requirement owners have a single source of truth for all functional requirements introduced to date.
- It supersedes **all prior requirement impact documents**; downstream artifacts (e.g., `docs/REQUIREMENTS.md`, traceability matrices, agent prompts) must now align with the definitions captured here.

## Updated Functional Requirements
| Requirement ID | Consolidated Update | Key Artifacts / Owners | Source CRs / CHs |
| --- | --- | --- | --- |
| FR-01 Project Manager | - Orchestrate the RA→IA→IM→QA→TQA→GO loop and coordinate Change Evaluator outcomes.<br>- Detect `maturity_level` from project metadata and activate only the agents required for that level.<br>- Maintain change metrics, maturity state, and ensure Governance Officer reports are consumed before approvals. | `agents/project_manager.py`, `PROJECT_METADATA.md`, change dashboards. | CR001–CR001.3 |
| FR-02 Status Documentation | - Embed per-change and maturity summaries in `PROJECT_OVERVIEW.md` / `PROJECT_DETAIL.md`.<br>- Cross-link to `CHANGELOG.md`, `IM_PROGRESS.md`, `GOVERNANCE_REPORT.md`, and maturity upgrade records. | PM agent, Governance Officer. | CR001.1–CR001.3 |
| FR-04 Implementation Governance | - Every execution path originates from a `CH-###` change anchor with lifecycle visibility (Draft → Approved → Merged).<br>- Implementer enforces a SpekKit-inspired micro-spec loop with deterministic task execution, evidence capture, and staged approvals.<br>- Partial approvals/denials route to FR-07 concern loops instead of resetting workstreams. | Implementer service, Implementation Manager, Governance Officer. | CH-001, CH-002, CH-004 |
| FR-05 Tester-Owned QA Artifacts | - Treat Test Quality Assessor as a standalone agent supplying risk-tier depth metrics.<br>- Incorporate risk-based coverage ratios, maturity band indicators, and Test Quality Summary tables in QA docs. | Tester agent, TQA agent, `tests/TEST_PLAN.md`. | CR001, CR001.1, CR001.3 |
| FR-06 Structured Handoffs & Audit Trails | - Extend audit entries with `{fr_id, ws_id, tc_id, raci_role, change_id, maturity_level, run_id, seed, artifact_hash, timestamp}`.<br>- Implementer run logs persist under `artifacts/work/CH-###/`, capturing tool versions and replay seeds.<br>- `/df.*` commands emit normalized JSON entries consumed by FR-06 ingestion. | Audit logger, Governance Officer, QA Lead. | CR001–CR001.3, CH-002 |
| FR-07 Concern Management | - Failed Implementer runs auto-raise FR-07 concerns tied to the originating change object.<br>- `/df.clarify` and `/df.analyze` surface traceability drift, unclipped documents, and reconciliation gaps.<br>- Rework loops resolve partial denials without discarding captured evidence. | Governance Officer, QA Auditor, Change Router. | CH-001, CH-003 |
| FR-10 Human Approval Gates | - Enforce multi-gate approvals: Impact Assessor → Change Evaluator (advisory) → Governance Officer → PM → Human Reviewer.<br>- Require Governance Officer sign-off from maturity level M2 upward and document satisfied criteria. | PM agent, Governance Officer, Human Reviewer. | CR001.1–CR001.3 |
| FR-11 QA Policy Engine | - Consume risk tiers, Implementer micro-task verdicts, `/df.checklist` outputs, and maturity thresholds before merges.<br>- Governance Officer sign-off precedes HR approval; QA blocks promotions while outstanding change objects lack complete staged approvals. | QA policy engine, Governance Officer, Human Reviewer. | CR001, CR001.2–CR001.3, CH-002, CH-004 |
| FR-13 Status Snapshots | - Report change density, change-to-delivery lag, vision drift indicators, stability ratio, and maturity level/time-in-level in status outputs.<br>- Surface metrics in Markdown snapshots and CLI dashboards. | PM agent, analytics tooling. | CR001, CR001.2–CR001.3 |

## New Functional Requirements
| Requirement ID | Requirement Summary | Primary Owner | Notes & Clarifications |
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
| FR-24 | Extend interaction CLI with `/impact`, `/trace`, `/change`, and `/approve` commands supporting offline and remote integrations (e.g., Discord). | Interaction Stub owner | Must operate locally and through integrations. |
| FR-25 | Maintain structured change workspaces (`changes/CH-###/` with `spec.md`, `plan.md`, `tasks.md`, `impact.md`, `evidence.json`, `status.md`) so every change remains synchronized with downstream artifacts. | Implementation Manager / Governance Officer | Ownership split confirmed; weekly IM↔GO sync validates state. |
| FR-26 | Enforce bidirectional traceability between FR/WS/TC artifacts and their associated change objects, tracking lifecycle states Draft → Analyzed → In-Progress → Partially Approved → Approved → Merged. | Governance Officer | Implementer updates `status.md`; Governance Officer governs transitions. |
| FR-27 | Manage ephemeral Implementer workspaces under `artifacts/work/CH-###/run-*`, auto-purging successful runs after 48 h or above 2 GB usage, retaining failures for 30 days, and honoring `--retain` markers. | Implementer Service | `.retain` marker opt-out approved; policy keeps storage lightweight. |
| FR-28 | Provide `/df.clarify`, `/df.analyze`, `/df.checklist`, and `dynaforge doctor` commands that emit JSON logs under `artifacts/analyze/`, validating traceability coverage and environment health. | QA Lead / Tooling | Command outputs standardized for FR-06 ingestion. |
| FR-29 | Reimplement SpekKit-inspired micro-task decomposition using planner/executor/cleanup modules, guaranteeing deterministic sequencing, evidence capture, and automatic cleanup on completion. | Implementer Service | No direct SpekKit code reuse; interfaces allow future planner upgrades. |
| FR-30 | Implement change velocity dashboard with weekly/milestone metrics accessible via CLI and dashboards. | PM / Analytics owner | Weekly cadence prioritized. |
| FR-31 | Support partial change approvals within a single `CH-###` record, tracking sub-decisions in evaluation docs. | Implementation Manager | Avoids branching change IDs. |
| FR-32 | Maintain `PROJECT_METADATA.md` (or `project.yaml`) capturing maturity level, last review, criteria, and next target level. | PM / Governance Officer | Single source for maturity-aware agents. |
| FR-33 | Publish `docs/PROCESS_MATURITY_GUIDE.md` describing maturity expectations and agent participation per level. | Governance Officer | Keep synchronized with project metadata. |
| FR-34 | Run maturity gate reviews, logging upgrade recommendations and outcomes as `CH-###` entries. | Governance Officer | Triggered per milestone or on demand. |
| FR-35 | Enable maturity-aware prompts/behavior for PM, GO, CE, IM, QA/TQA, and related agents. | Platform / Agent Owners | Requires shared libraries and regression tests. |
| FR-36 | Track maturity metrics (time-in-level, upgrade count, active criteria) and surface them in `PROJECT_OVERVIEW.md` and CLI `/status`. | PM / Analytics owner | Permanent record plus quick CLI access. |
| FR-37 | Produce approved requirement elaboration files (`docs/requirements/elaborations/FR-###_elaboration.md`) before implementation; ensure HR/GO approvals precede Implementation Manager workstream decomposition. | Requirement Elaboration Agent / Governance Officer | Implementation Manager must not create `WS-*` entries prior to approval. |

## Traceability, Change, and Governance Artifacts
- `TRACEABILITY.md` must include risk classifications, `### Unmapped Elements`, `### Test Quality Summary`, `### Artifact Integrity`, metrics footers, and references to associated `CH-###` entries.
- `CHANGELOG.md` records every change object, including maturity upgrades, partial approvals, and reconciliation notes.
- `IMPACT_REPORT.md`, `IM_PROGRESS.md`, and `GOVERNANCE_REPORT.md` capture change impact, task execution, and compliance evidence respectively.
- Requirement elaborations reside in `docs/requirements/elaborations/` and must be approved per FR-37 before Implementation Manager decomposes workstreams.
- `PROJECT_METADATA.md` stores maturity level, last review date, readiness criteria, and next target level; agents read this to adjust enforcement.
- Audit logs (`audit/*.jsonl`) append `change_id`, `lifecycle_state`, and content hashes for reproducibility and FR-06 ingestion.

### Clipped Documents Governance Addendum
| Aspect | Benefit |
| --- | --- |
| Traceability | Verifies that ideation artifacts have been incorporated into baseline requirements and traceability assets. |
| Visual Clarity | Quick folder scans distinguish active vs archived documents without relocation overhead. |
| Automation | Tooling can ignore `_c_*` prefixed files while still flagging unclipped sources needing incorporation. |
| Provenance | Preserves historical context for audits and retrospectives without deleting artifacts. |
| Flow Discipline | Reinforces the idea → design → architecture → implementation progression by marking completion points. |

**Process Convention**
- Active documents retain their original filenames (e.g., `design_microservices.md`).
- Once incorporated, prepend `_c_` to mark the document as clipped (e.g., `_c_design_microservices.md`).
- Tooling integrations:
  - Add `_c_*` patterns to `.specignore`, `.codexignore`, and `dynaforge.yaml` to exclude clipped docs from active agent sweeps.
  - Optional `dynaforge clip` helper can automate renaming, append a YAML footer, and log provenance to `TRACEABILITY.md` under “Source Documents”.
- Optional YAML footer for clipped docs:
  ```yaml
  ---
  status: clipped
  incorporated_into:
    - docs/requirements.md
    - docs/traceability.md
  date_clipped: 2025-11-01
  ```

## Decision Log & Clarifications
- **Change Evaluator Thresholds:** AI provides ROI/value vs disruption recommendations; human reviewers make the final decision (ROI ≥ 1.5 suggested but not mandatory).
- **Partial Approvals:** Track sub-decisions inside a single change object (`CH-###`) instead of branching IDs.
- **Vision Validator Role:** Remains advisory; feeds change evaluation without automatic blocking.
- **CLI Commands:** `/impact`, `/change`, `/trace`, `/approve` operate both offline and via remote integrations.
- **Maturity Reviews:** Conduct per milestone (or on request) with Governance Officer leadership; automation can downgrade if criteria regress.
- **Downgrades:** Supported; agents revert to lighter processes automatically while preserving historical evidence.
- **Maturity Metrics Visibility:** Required in `PROJECT_OVERVIEW.md` and CLI `/status` for rapid assessment.
- **Requirement Elaborations:** Implementation Manager must not create `WS-*` entries until the corresponding elaboration file is marked Approved by HR and GO.

## Resolved Follow-ups
- **Ownership Split:** Governance Officer manages lifecycle enforcement (state transitions, approvals, reconciliation checks) while the Implementation Manager maintains the durable change workspace and aligns Implementer runs with the active change. Weekly IM↔GO sync confirms state accuracy before HR approvals.
- **Ephemeral Retention Policy:** Successful Implementer runs purge automatically when older than 48 hours or when `artifacts/work/` exceeds 2 GB. Failed runs persist for 30 days. The `--retain` flag writes a `.retain` marker that pauses cleanup until cleared.
- **Audit Event Schema:** Standardize on JSONL entries with `{ ch_id, run_id, lifecycle_state, event_type, actor, timestamp, status, step, fr_refs[], ws_refs[], tc_refs[], files[], metrics{ duration_ms, assertions, coverage }, seed, command, notes }`. `/df.*` commands emit `event_type` values such as `df.clarify.summary`, ensuring uniform ingestion.
- **Staged Approval Alignment:** Implementer sets `status.md` to `Partially Approved` after IM and QA checks succeed; Governance Officer marks `Approved` once compliance criteria pass, and HR completes merge authorization. Denials reopen the change via FR-07 concerns, preserving audit continuity.
- **SpekKit-Inspired Loop Design:** Planner, executor, and cleanup modules expose stable interfaces so future heuristic upgrades can replace the planner without refactoring execution. The implementation reimagines SpekKit concepts without importing its codebase.

## Metadata File Strategy (Adopted)
| Approach | Pros | Cons |
| --- | --- | --- |
| **Single repo-level `PROJECT_METADATA.md`** | Simple to maintain; single truth for agents and dashboards; easy prompt caching. | Mixed phases share maturity state; needs additional fields to distinguish concurrent efforts. |
| **Per project/phase metadata file (e.g., `projects/<id>/metadata.yaml`)** | Enables parallel initiatives with independent maturity levels; supports historical snapshots by phase. | Higher coordination overhead; agents must resolve active project scope; risk of drift if files diverge. |

**Decision:** Adopt a **single repo-level `PROJECT_METADATA.md`** containing an array of active projects/phases. Example:
```yaml
projects:
  - name: "dynaforge.ai"
    phase: phase-1
    maturity_level: M2
    last_review: 2025-10-30
    next_target_level: M3
    criteria:
      value_proven: true
      governance_enabled: true
  - name: "dynaforge.ai"
    phase: phase-0
    maturity_level: Archived
```
Agents read the entry matching the active phase (declared in prompts or task context) and fall back to default rules if no match exists.

## Next Actions
1. Update `docs/REQUIREMENTS.md` and related traceability assets to reflect all updates in this document.
2. Implement `_c_*` ignore patterns and optional `dynaforge clip` helper to operationalize the clipping convention.
3. Stand up the normalized audit schema across Implementer, `/df.*` tooling, and Governance Officer pipelines.
4. Plan rollout for maturity-aware agent prompts, prioritizing Governance Officer, QA Auditor, and Implementer integrations.
