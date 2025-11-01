# Traceability Matrix

_Last updated: 2025-11-01 — maintained by Codex agent._

## Legend
- Workstream status: `DONE` (delivered), `IN PROGRESS` (currently active), `PLANNED` (not started), `CHANGE IMPACTED` (previously delivered but a new change requires rework before reuse).
- Requirement status: `DONE` (implemented with evidence), `PARTIAL` (in progress or partially validated), `IN PROGRESS` (active work), `PLANNED` (not yet implemented).
- Test status: `PASS` (evidence recorded), `PENDING` (test exists but not yet executed or captured), `TODO` (test not implemented).

## Milestone Strategy
- A milestone is a curated slice of requirements across phases that results in a system a human can exercise end-to-end; it must be testable and usable, even if only a small subset of total scope is complete.
- Milestones may take the form of spikes/POCs, betas, or full releases. Percent completion of requirements is less important than demonstrating a coherent workflow a real user can trial.
- Delivery cadence is driven by the human stakeholder: we request the next milestone definition from them and focus the workstreams, requirements, and tests in this matrix around that target until accepted.
- **Current target milestone — POC Spike:** stand up the minimum set of agents and integrations required to exhibit a working Dynaforge loop, establishing a usable foundation for future increments.

### MS-01 — POC Spike (Minimum Agent Loop)
- `Identifier`: MS-01
- `Objective`: Prove the Dynaforge core by wiring the minimum agent chain (PM → Designer → Implementer → Tester) with human-visible logging, approvals, and demo collateral.
- `Scope guidance`: Focus on workstreams that enable a human to run, observe, and judge the loop. Deferrable items (e.g., maturity scoring, governance automation) stay out of scope until the next milestone request.

| Phase | Workstream | Role in MS-01 | Current Status |
| --- | --- | --- | --- |
| Phase 0 — Foundation | WS-01 Repository Skeleton | Provides the repo layout, docs, and scaffolding the agents reference during the demo. | CHANGE IMPACTED |
| Phase 0 — Foundation | WS-02 Audit Logging Primitives | Captures evidence of each agent handoff so the spike is testable and reviewable. | CHANGE IMPACTED |
| Phase 0 — Foundation | WS-04 Interaction Stub | Supplies the human interaction surface for issuing `/status` and `/clarify` during the spike. | DONE |
| Phase 0 — Foundation | WS-05 Project Manager Skeleton | Enables the PM agent logic that anchors the orchestrated loop. | CHANGE IMPACTED |
| Phase 0 — Foundation | WS-07 Demo Workflow Target | Bundles artifacts that demonstrate the spike end-to-end for stakeholder validation. | CHANGE IMPACTED |
| Phase 0 — Foundation | WS-08 Documentation Updates | Keeps human-facing docs aligned with the spike’s behavior for acceptance. | CHANGE IMPACTED |
| Phase 1 — Core Agent Loop | WS-101 Multi-Agent Orchestration | Drives the PM→Designer→Implementer→Tester cycle showcased in the spike. | CHANGE IMPACTED |
| Phase 1 — Core Agent Loop | WS-103 Human Approval Gates | Ensures the human can approve/deny progression, making the spike truly usable. | CHANGE IMPACTED |
| Phase 1 — Core Agent Loop | WS-105 Interaction Bridge Expansion | Adds the command coverage needed for a realistic human-agent exchange. | DONE |
| Phase 1 — Core Agent Loop | WS-108 Demo & Documentation | Packages the walkthrough and narrative that explain how to operate the spike. | IN PROGRESS |
| Phase 1 — Core Agent Loop | WS-109 Implementer Micro-Loop & Retention | Aligns the Implementer micro-loop and artifact retention with CR002 governance expectations. | CHANGE IMPACTED |

> _MS-01 readiness note:_ All statuses below reflect whether each stream or requirement is ready for the refreshed MS-01 milestone run; anything marked `CHANGE IMPACTED` or `PARTIAL` still needs a new execution pass before acceptance.

---

## Phase 0 — Foundation

| Workstream | Status | Related Requirements | Evidence |
| --- | --- | --- | --- |
| WS-01 Repository Skeleton | CHANGE IMPACTED | FR-01, FR-02 | Repository structure and docs seeded (`docs/PHASE0_PLAN.md`) |
| WS-02 Audit Logging Primitives | CHANGE IMPACTED | FR-06, FR-09 | JSONL logger and sample artifacts (`audit/logger.py`, `audit/sample_handoff.jsonl`) |
| WS-03 Concern API & Schema Docs | PARTIAL | FR-07 | Concern helpers exported; schema documented in workflow guide (`docs/WORKFLOW.md`) |
| WS-04 Interaction Stub | DONE | FR-08, FR-09 | CLI stub with `/status` and `/clarify` wired to logging (`pipelines/interaction_stub.py`) |
| WS-05 Project Manager Skeleton | CHANGE IMPACTED | FR-01, FR-02 | PM agent updates docs and logs handoffs (`agents/project_manager.py`) |
| WS-06 QA Policy Parser Stub | PARTIAL | FR-11 | Parser stub plus unit tests (TC-FR11-001, `pipelines/policy_parser.py`) |
| WS-07 Demo Workflow Target | CHANGE IMPACTED | FR-01, FR-06, FR-09 | `make demo` artifacts (`artifacts/phase0/demo/`) |
| WS-08 Documentation Updates | CHANGE IMPACTED | FR-02, FR-10 | Docs refreshed with approval markers (`docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_DETAIL.md`) |

### WS-01 Repository Skeleton

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-01 Project Manager agent scaffolding | PARTIAL | TC-FR01-001 | PASS | Baseline directories and docs enable PM agent; integration test confirms doc refresh and audit handoff wiring. |
| FR-02 Status documentation maintained | PARTIAL | TC-FR01-001 | PASS | Docs were current for Phase 0; MS-01 refresh pending updated workflow evidence. |

### WS-02 Audit Logging Primitives

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-06 Handoff logging | PARTIAL | TC-FR06-001 | PASS | Logger proven in Phase 0; rerun required to capture refreshed MS-01 workflow evidence. |
| FR-09 Command audit trail | PARTIAL | TC-FR06-001 | PASS | Helpers work, but audit artifacts need regeneration after milestone reset. |

### WS-03 Concern API & Schema Docs

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-07 Concern logging and mirroring | PARTIAL | TC-FR07-001 | PASS | Concern helpers exist; unit test exercises raise/update/resolve with Markdown sync. |

### WS-04 Interaction Stub

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-08 Discord bridge commands (`/status`, `/clarify`) | DONE | TC-FR08-001 | PASS | Stub responds deterministically; audit entries recorded in `audit/commands.jsonl`. |
| FR-09 Command routing + logging | DONE | TC-FR09-001 | PASS | CLI writes structured command events consumed in Phase 1 demos. |

### WS-05 Project Manager Skeleton

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-01 Project Manager coordination | PARTIAL | TC-FR01-001, TC-FR01-002 | PASS | Phase 0 PM updates docs; orchestration and doc refresh verified via integration coverage. |
| FR-02 Status documentation maintained | PARTIAL | TC-FR01-001 | PASS | Automation exists, but docs need a new MS-01 run before claiming completion. |
| FR-10 Approval capture | PARTIAL | TC-FR10-001 | PASS | Approval markers defined; enforcement completed under Phase 1 WS-103 with passing unit test. |

### WS-06 QA Policy Parser Stub

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-11 QA policy enforcement | PARTIAL | TC-FR11-001 | PASS | Parser validates schema; enforcement engine slated for Phase 1 WS-104. |

### WS-07 Demo Workflow Target

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-01 Orchestrated PM cycle | PARTIAL | TC-FR01-002 | PASS | Demo exercises PM + logging; integration test executes orchestrator and verifies artifact bundle. |
| FR-06 Handoff logging completeness | PARTIAL | TC-FR06-001 | PASS | Demo run validated Phase 0; MS-01 demo package must be rerun to confirm coverage. |
| FR-09 Command audit trail | PARTIAL | TC-FR09-001 | PASS | Command log exists, but updated demo bundle is pending after the reset. |

### WS-08 Documentation Updates

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-02 Documentation currency | PARTIAL | TC-FR01-001 | PASS | Phase 0 alignment proven; needs MS-01 updates before we report DONE again. |
| FR-10 Approval markers | PARTIAL | TC-FR10-001 | PASS | Approval checklist established; enforcement validated in Phase 1. |

---

## Phase 1 — Core Agent Loop

| Workstream | Status | Related Requirements | Evidence |
| --- | --- | --- | --- |
| WS-101 Multi-Agent Orchestration | CHANGE IMPACTED | FR-01, FR-04, FR-06 | Orchestrator loop artifacts (`artifacts/phase1/orchestration/run.log`) |
| WS-102 Concern Lifecycle | IN PROGRESS | FR-07 | Concern toolkit foundations (`pipelines/concern_tools.py`) |
| WS-103 Human Approval Gates | CHANGE IMPACTED | FR-10 | Approval enforcement tests (TC-FR10-001, `artifacts/phase1/approvals/denied.txt`) |
| WS-104 QA Policy Enforcement | PLANNED | FR-11 | Pending implementation (see `PROGRESS.md`) |
| WS-105 Interaction Bridge Expansion | DONE | FR-08, FR-09 | Extended commands + audit logs (`pipelines/interaction_stub.py`, `artifacts/phase1/commands/`) |
| WS-106 Status Snapshots & Observability | PLANNED | FR-13 | Pending orchestration hook |
| WS-107 Rollback & Pause Controls | PLANNED | FR-14 | Scripts not yet implemented |
| WS-108 Demo & Documentation | IN PROGRESS | FR-02, FR-10 | Documentation refresh pending completion of WS-104–WS-107 |
| WS-109 Implementer Micro-Loop & Retention | CHANGE IMPACTED | FR-04, FR-27, FR-29 | CR002 realigns micro-loop enforcement and retention; design updates slated in `docs/REQUIREMENTS_1_2.md` |

### WS-101 Multi-Agent Orchestration

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-01 Project Manager coordinates agents | PARTIAL | TC-FR01-002 | PASS | Orchestrator sequencing validated once; needs MS-01 rerun to reconfirm handoffs. |
| FR-04 Implementer alignment with design | PARTIAL | TC-FR04-001 | PASS | Implementer hooks scaffolded; full enforcement of branch policy outstanding. |
| FR-06 Handoff logging (loop) | PARTIAL | TC-FR06-001 | PASS | Existing run logs cover earlier spike; updated MS-01 orchestration artifacts still outstanding. |

### WS-102 Concern Lifecycle

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-07 Concern lifecycle automation | PARTIAL | TC-FR07-001 | PASS | Unit test raises, updates, resolves concerns and mirrors Markdown; integration demo still pending. |

### WS-103 Human Approval Gates

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-10 Approval enforcement | PARTIAL | TC-FR10-001 | PASS | Enforcement logic exists, but MS-01 approval artifacts must be regenerated before we close it. |

### WS-104 QA Policy Enforcement

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-11 QA policy gating | PLANNED | TC-FR11-001 (PASS), TC-FR11-002 (TODO) | PARTIAL | Enforcement CLI not yet integrated; schema validation passes while enforcement coverage is pending. |

### WS-105 Interaction Bridge Expansion

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-08 Discord command coverage (`/ack`, `/resolve`, etc.) | PARTIAL | TC-FR08-001 (PASS), TC-FR08-002 (TODO) | PARTIAL | Command handlers implemented; manual command replay demo outstanding. |
| FR-09 Command routing + logging | DONE | TC-FR09-001 | PASS | Each command writes structured event files in `artifacts/phase1/commands/`. |

### WS-106 Status Snapshots & Observability

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-13 Status snapshots | PLANNED | TC-FR13-001 | TODO | Snapshot tooling slated for upcoming sprint; no implementation yet. |

### WS-107 Rollback & Pause Controls

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-14 Pause/resume & rollback | PLANNED | TC-FR14-001 | TODO | Pause/resume scripts and audits to be added. |

### WS-108 Demo & Documentation

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-02 Documentation currency | PARTIAL | TC-FR01-001 | PASS | Documentation will be refreshed post QA enforcement and status snapshot delivery. |
| FR-10 Approval capture | PARTIAL | TC-FR10-001 | PASS | Approval markers recorded; final demo sign-off pending completion of remaining workstreams. |

### WS-109 Implementer Micro-Loop & Retention

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-04 Implementation governance micro-loop | PARTIAL | TC-FR04-001, TC-FR04-002 (TODO) | PARTIAL | Implementer loop executes deterministically for core path; CR002 updates captured in `docs/REQUIREMENTS_1_2.md` require planner/executor refinements. |
| FR-27 Implementer run retention | PLANNED | TC-FR27-001 (TODO) | TODO | Retention policy must auto-purge successful runs after 48 h/2 GB and respect `.retain` markers. |
| FR-29 SpekKit-inspired micro-task loop | PLANNED | TC-FR29-001 (TODO) | TODO | Planner/executor/cleanup modules to reimplement SpekKit concepts without code reuse. |

---

## Phase 2 — Change Governance Loop

| Workstream | Status | Related Requirements | Evidence |
| --- | --- | --- | --- |
| WS-201 Requirements Intelligence | PLANNED | FR-02, FR-15, FR-26, FR-37 | Scope captured in `docs/REQUIREMENTS_1_2.md` |
| WS-202 Impact Assessment & Evaluator | PLANNED | FR-16 | Planned artifacts: `IMPACT_REPORT.md`, impact scoring heuristics |
| WS-203 Implementation Management | PLANNED | FR-21, FR-25, FR-31 | Implementation Manager brief (`IM_PROGRESS.md`) to be authored |
| WS-204 Governance & Multi-Gate Approvals | PLANNED | FR-10, FR-22, FR-34 | Governance Officer charter (`GOVERNANCE_REPORT.md`) pending |
| WS-205 Change Router & Orchestration | PLANNED | FR-01, FR-23 | Change router design notes (`docs/REQUIREMENTS_1_2.md`) |
| WS-206 Change Records & Audit Extensions | PLANNED | FR-06, FR-20, FR-26 | Audit schema expansion plan (`audit/`) to be drafted |
| WS-207 Interaction CLI Extensions | PLANNED | FR-24, FR-28 | `/impact`, `/trace`, `/df.*` CLI specs (planned) |

### WS-201 Requirements Intelligence

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-02 Status documentation (maturity summaries) | PLANNED | TC-FR02-002 | TODO | Expand docs with per-change + maturity cross-links. |
| FR-15 Requirements Analyst agent | PLANNED | TC-FR15-001 | TODO | RA agent updates traceability and flags ripple risks. |
| FR-26 Bidirectional change traceability | PLANNED | TC-FR26-001 | TODO | Ensure FR/WS/TC artifacts link to `CH-###` records with lifecycle states. |
| FR-37 Requirement elaboration workflow | PLANNED | TC-FR37-001 | TODO | Approved elaborations gate workstream creation. |

### WS-202 Impact Assessment & Evaluator

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-16 Impact Assessor agent | PLANNED | TC-FR16-001 | TODO | Quantifies downstream effects and maintains `IMPACT_REPORT.md`. |

### WS-203 Implementation Management

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-21 Implementation Manager agent | PLANNED | TC-FR21-001 | TODO | Decomposes objectives into `WS-*` with evidence tracking. |
| FR-25 Change workspace management | PLANNED | TC-FR25-001 | TODO | Maintain `changes/CH-###/` bundles with `spec.md`, `plan.md`, `tasks.md`, `impact.md`, `evidence.json`, `status.md`. |
| FR-31 Partial change approvals | PLANNED | TC-FR31-001 | TODO | Track sub-decisions within `CH-###` records. |

### WS-204 Governance & Multi-Gate Approvals

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-10 Approval governance (expanded gates) | PLANNED | TC-FR10-002 | TODO | Enforce advisory/governance officer/human review sequence. |
| FR-22 Governance Officer agent | PLANNED | TC-FR22-001 | TODO | Oversees QA/TQA and publishes `GOVERNANCE_REPORT.md`. |
| FR-34 Maturity gate reviews | PLANNED | TC-FR34-001 | TODO | Log upgrade outcomes as `CH-###` entries. |

### WS-205 Change Router & Orchestration

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-01 Project Manager (governance loop orchestration) | PLANNED | TC-FR01-003 | TODO | Trigger RA→IA→IM→QA→TQA→GO loop per change. |
| FR-23 Automated orchestration triggers | PLANNED | TC-FR23-001 | TODO | Fire orchestration on requirement/doc deltas. |

### WS-206 Change Records & Audit Extensions

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-06 Structured handoff logging (extended schema) | PLANNED | TC-FR06-002 | TODO | Append change/maturity metadata to audit logs. |
| FR-20 RACI metadata propagation | PLANNED | TC-FR20-001 | TODO | Embed `raci_role` in audit logs and artifacts. |
| FR-26 Bidirectional change traceability | PLANNED | TC-FR26-001 | TODO | Ensure `CH-###` entries and FR/WS/TC artifacts cross-link with lifecycle state tracking. |

### WS-207 Interaction CLI Extensions

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-24 `/impact` and `/trace` commands | PLANNED | TC-FR24-001 | TODO | Support local and remote (Discord) contexts. |
| FR-28 `/df.clarify`, `/df.analyze`, `/df.checklist`, `dynaforge doctor` | PLANNED | TC-FR28-001 | TODO | Emit JSON logs under `artifacts/analyze/` for FR-06 ingestion. |

---

## Phase 3 — QA & Maturity Automation

| Workstream | Status | Related Requirements | Evidence |
| --- | --- | --- | --- |
| WS-301 QA Auditor & Traceability Gaps | PLANNED | FR-17 | Traceability gap workflow scoped in `docs/REQUIREMENTS_1_2.md` |
| WS-302 Test Synthesizer & Quality Depth | PLANNED | FR-05, FR-18, FR-19 | QA/Test agent briefs (`tests/`) to be generated |
| WS-303 QA Policy Engine Enhancements | PLANNED | FR-11 | Policy engine design update pending |
| WS-304 Maturity Metadata & Guides | PLANNED | FR-32, FR-33 | `PROJECT_METADATA.md`, `PROCESS_MATURITY_GUIDE.md` planned |
| WS-305 Maturity-Aware Agent Prompts | PLANNED | FR-35 | Prompt adaptation backlog item |
| WS-306 Maturity Metrics & Snapshots | PLANNED | FR-13, FR-30, FR-36 | Metrics dashboard plan upcoming |

### WS-301 QA Auditor & Traceability Gaps

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-17 QA Auditor agent | PLANNED | TC-FR17-001 | TODO | Generate traceability gap reports with risk tiers. |

### WS-302 Test Synthesizer & Quality Depth

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-05 Tester-owned QA artifacts (risk depth) | PLANNED | TC-FR05-002 | TODO | Incorporate TQA metrics and depth tables. |
| FR-18 Test Synthesizer agent | PLANNED | TC-FR18-001 | TODO | Generate/update `TC-*` artifacts from impact outputs. |
| FR-19 Test Quality Assessor | PLANNED | TC-FR19-001 | TODO | Deliver risk-based coverage ratios and summaries. |

### WS-303 QA Policy Engine Enhancements

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-11 QA policy engine (maturity-aware gating) | PLANNED | TC-FR11-003 | TODO | Consume risk tiers and maturity thresholds before merges. |

### WS-304 Maturity Metadata & Guides

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-32 Project metadata source (`PROJECT_METADATA.md`) | PLANNED | TC-FR32-001 | TODO | Capture maturity level, review history, criteria. |
| FR-33 Process maturity guide | PLANNED | TC-FR33-001 | TODO | Document expectations and agent participation per level. |

### WS-305 Maturity-Aware Agent Prompts

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-35 Maturity-aware agent prompts | PLANNED | TC-FR35-001 | TODO | Adapt prompts for PM, GO, CE, IM, QA/TQA. |

### WS-306 Maturity Metrics & Snapshots

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-13 Status snapshots (metrics expansion) | PLANNED | TC-FR13-002 | TODO | Surface change density, lag, drift, stability ratio. |
| FR-30 Change velocity dashboard | PLANNED | TC-FR30-001 | TODO | Weekly/milestone metrics accessible via CLI/dashboards. |
| FR-36 Maturity metrics tracking | PLANNED | TC-FR36-001 | TODO | Track time-in-level, upgrade count, active criteria. |

---

## Overview by Requirement

| Requirement | Current Status | Validating Workstreams | Primary Tests / Evidence |
| --- | --- | --- | --- |
| FR-01 Project Manager agent coordination | PARTIAL | WS-01, WS-05, WS-07, WS-101, WS-205 | TC-FR01-001, TC-FR01-002, TC-FR01-003 (TODO), `artifacts/phase1/orchestration/run.log` |
| FR-02 Status documentation | PARTIAL | WS-01, WS-05, WS-08, WS-108, WS-201 | TC-FR01-001, TC-FR02-002 (TODO), `docs/PROJECT_OVERVIEW.md` |
| FR-03 Designer agent deliverables | PARTIAL | WS-101 | TC-FR03-001, `design/DESIGN_SPEC.md` |
| FR-04 Implementer branch + artifact discipline | PARTIAL | WS-101 | TC-FR04-001, `docs/IMPLEMENTATION_PLAN.md` |
| FR-05 Tester-owned QA artifacts | PARTIAL | WS-104, WS-302 | TC-FR05-001, TC-FR05-002 (TODO), `tests/TEST_PLAN.md` |
| FR-06 Handoff logging | PARTIAL | WS-02, WS-04, WS-07, WS-101, WS-206 | TC-FR06-001, TC-FR06-002 (TODO), `artifacts/phase0/demo/` |
| FR-07 Concern lifecycle | PARTIAL | WS-03, WS-102 | TC-FR07-001, `pipelines/concern_tools.py` |
| FR-08 Discord bridge commands | PARTIAL | WS-04, WS-105 | TC-FR08-001, TC-FR08-002 (TODO), `artifacts/phase1/commands/` |
| FR-09 Command audit trail | PARTIAL | WS-02, WS-04, WS-05, WS-105 | TC-FR09-001, `audit/commands.jsonl` |
| FR-10 Approval governance | PARTIAL | WS-05, WS-08, WS-103, WS-108, WS-204 | TC-FR10-001, TC-FR10-002 (TODO), `artifacts/phase1/approvals/denied.txt` |
| FR-11 QA policy enforcement | PARTIAL | WS-06, WS-104, WS-303 | TC-FR11-001, TC-FR11-002 (TODO), TC-FR11-003 (TODO) |
| FR-12 GitOps workflow controls | PLANNED | Future phase | TC-FR12-001 (TODO) |
| FR-13 Status snapshots | PLANNED | WS-106, WS-306 | TC-FR13-001 (TODO), TC-FR13-002 (TODO) |
| FR-14 Rollback & pause controls | PLANNED | WS-107 | TC-FR14-001 (TODO) |
| FR-15 Requirements Analyst agent | PLANNED | WS-201 | TC-FR15-001 (TODO) |
| FR-16 Impact Assessor agent | PLANNED | WS-202 | TC-FR16-001 (TODO) |
| FR-17 QA Auditor agent | PLANNED | WS-301 | TC-FR17-001 (TODO) |
| FR-18 Test Synthesizer agent | PLANNED | WS-302 | TC-FR18-001 (TODO) |
| FR-19 Test Quality Assessor | PLANNED | WS-302 | TC-FR19-001 (TODO) |
| FR-20 RACI metadata propagation | PLANNED | WS-206 | TC-FR20-001 (TODO) |
| FR-21 Implementation Manager agent | PLANNED | WS-203 | TC-FR21-001 (TODO) |
| FR-22 Governance Officer agent | PLANNED | WS-204 | TC-FR22-001 (TODO) |
| FR-23 Automated orchestration triggers | PLANNED | WS-205 | TC-FR23-001 (TODO) |
| FR-24 `/impact` and `/trace` commands | PLANNED | WS-207 | TC-FR24-001 (TODO) |
| FR-25 Change workspace management | PLANNED | WS-203 | TC-FR25-001 (TODO), `changes/CH-###/` template plan |
| FR-26 Bidirectional change traceability | PLANNED | WS-201, WS-206 | TC-FR26-001 (TODO), `TRACEABILITY.md` updates |
| FR-27 Implementer run retention | PLANNED | WS-109 | TC-FR27-001 (TODO), retention policy spec |
| FR-28 `/df.*` analysis commands | PLANNED | WS-207 | TC-FR28-001 (TODO), `/df.*` CLI design notes |
| FR-29 SpekKit-inspired micro-task loop | PLANNED | WS-109 | TC-FR29-001 (TODO), planner/executor design draft |
| FR-30 Change velocity dashboard | PLANNED | WS-306 | TC-FR30-001 (TODO) |
| FR-31 Partial change approvals | PLANNED | WS-203 | TC-FR31-001 (TODO) |
| FR-32 Project metadata source | PLANNED | WS-304 | TC-FR32-001 (TODO) |
| FR-33 Process maturity guide | PLANNED | WS-304 | TC-FR33-001 (TODO) |
| FR-34 Maturity gate reviews | PLANNED | WS-204 | TC-FR34-001 (TODO) |
| FR-35 Maturity-aware agent prompts | PLANNED | WS-305 | TC-FR35-001 (TODO) |
| FR-36 Maturity metrics tracking | PLANNED | WS-306 | TC-FR36-001 (TODO) |
| FR-37 Requirement elaboration workflow | PLANNED | WS-201 | TC-FR37-001 (TODO) |
