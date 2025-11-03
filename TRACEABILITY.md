# Traceability Matrix

_Last updated: 2025-11-04 — maintained by Codex agent._

## Legend
- Workstream status: `DONE` (delivered), `IN PROGRESS` (currently active), `PLANNED` (not started), `CHANGE IMPACTED` (previously delivered but a new change requires rework before reuse).
- Requirement status: `DONE` (implemented with evidence), `PARTIAL` (in progress or partially validated), `IN PROGRESS` (active work), `PLANNED` (not yet implemented).
- Test status: `PASS` (evidence recorded), `PENDING` (test exists but not yet executed or captured), `TODO` (test not implemented).

## Milestone Strategy
- A milestone is a curated slice of requirements across phases that results in a system a human can exercise end-to-end; it must be testable and usable, even if only a small subset of total scope is complete.
- Milestones may take the form of spikes/POCs, betas, or full releases. Percent completion of requirements is less important than demonstrating a coherent workflow a real user can trial.
- Delivery cadence is driven by the human stakeholder: we request the next milestone definition from them and focus the workstreams, requirements, and tests in this matrix around that target until accepted.
- **Current target milestone — MS-02 Discovery MVP:** ship the discovery-first workflow captured in `design/MS-02_storyboard.md`, flowing from context intake through loop planning into the established MS-01 execution rail.

### MS-01 — POC Spike (Minimum Agent Loop)
- `Identifier`: MS-01
- `Objective`: Prove the Codexa core by wiring the minimum agent chain (PM → Designer → Implementer → Tester) with human-visible logging, approvals, and demo collateral.
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

### MS-02 — Discovery MVP
- `Identifier`: MS-02
- `Objective`: Deliver a runnable discovery pipeline that produces repo-tracked manifests, System Model Graph projections, understanding metrics, and seeded change journeys.
- `Scope guidance`: Prioritize quick/deep discovery modes, YAML projections as canonical artifacts, understanding coverage instrumentation, and the first `codexa seed` workflow. Advanced visualization and runtime probes remain out of scope for this milestone.

| Phase | Workstream | Role in MS-02 | Current Status |
| --- | --- | --- | --- |
| Phase 0 — Foundation | WS-09 Discovery Foundations | Implement discovery config/telemetry, iteration logging, and System Model Graph refresh hooks. | IN PROGRESS |
| Phase 1 — Core Agent Loop | WS-110 Loop Planning & Seed Generation | Deliver prompt-first `codexa loop plan` and `codexa seed --from loop-plan` packaging that feeds execution scope. | IN PROGRESS |
| Phase 2 — Change Governance Loop | WS-201 Requirements Intelligence | Normalise curated requirement inputs, link to discovery artifacts, and update traceability/gaps dashboards. | IN PROGRESS |
| Phase 2 — Change Governance Loop | WS-202 Impact Assessment & Evaluator | Incorporate readiness heatmaps and conversational follow-up handling into impact scoring. | IN PROGRESS |
| Phase 3 — QA & Maturity Automation | WS-306 Maturity Metrics & Snapshots | Surface understanding coverage within `/status`, governance summaries, and milestone storyboard outputs. | IN PROGRESS |

> _MS-02 readiness note:_ Demo readiness is reached when:
> - Discovery runs via `codexa discover --config docs/discovery/config.yaml` populate manifests + System Model Graph, stream telemetry, and append follow-ups to `docs/status/iteration_log.md`.
> - Humans can select execution scope through the loop-planning conversation (requirement/change/phase/milestone), with the plan captured in `loop-plan.json`.
> - `codexa seed --from loop-plan` produces the scoped bundle and conversational review gates record approvals or waivers in `changes/CH-###/seed/REVIEW.md`.
> - Governance summary prompts (`summary.md` / `gaps.md`) publish successfully with no outstanding mandatory gaps.
> See `design/MS-02_storyboard.md` for the golden-path narrative and artifact cross-links.

---

## Phase 0 — Foundation

| Workstream | Status | Related Requirements | Evidence |
| --- | --- | --- | --- |
| WS-01 Repository Skeleton | DONE | FR-01, FR-02 | Phase 0 regeneration captured (`artifacts/work/CH-001/run-01/manifest.json`, `docs/PROJECT_OVERVIEW.md`) |
| WS-02 Audit Logging Primitives | DONE | FR-06, FR-09 | CH-001 audit replay (`artifacts/work/CH-001/run-02/manifest.json`, `audit/handoff_ms01_phase0.jsonl`) |
| WS-03 Concern API & Schema Docs | PARTIAL | FR-07 | Concern helpers exported; schema documented in workflow guide (`docs/WORKFLOW.md`) |
| WS-04 Interaction Stub | DONE | FR-08, FR-09 | CLI stub with `/status` and `/clarify` wired to logging (`pipelines/interaction_stub.py`) |
| WS-05 Project Manager Skeleton | DONE | FR-01, FR-02 | PM orchestrator rerun (`artifacts/work/CH-001/run-04/manifest.json`, `docs/IMPLEMENTATION_PLAN.md`) |
| WS-06 QA Policy Parser Stub | PARTIAL | FR-11 | Parser stub plus unit tests (TC-FR11-001, `pipelines/policy_parser.py`) |
| WS-07 Demo Workflow Target | DONE | FR-01, FR-06, FR-09 | Deterministic demo package (`artifacts/phase0/demo/2025-11-02/README.md`) |
| WS-08 Documentation Updates | DONE | FR-02, FR-10 | Documentation aligned to CH-001 (`docs/PROJECT_DETAIL.md`, `docs/VERSION_CONTROL.md`) |
| WS-09 Discovery Foundations | IN PROGRESS | FR-38, FR-39, FR-41 | Discovery config + telemetry + iteration log (`docs/discovery/config.yaml`, `docs/status/iteration_log.md`, `design/MS-02_storyboard.md#stage-2`) |

### WS-01 Repository Skeleton

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-01 Project Manager agent scaffolding | DONE | TC-FR01-001 | PASS | CH-001 run (`artifacts/work/CH-001/run-01/manifest.json`) refreshed docs and logged handoff with new evidence. |
| FR-02 Status documentation maintained | DONE | TC-FR01-001 | PASS | Documentation updated via CH-001 Package prep (`docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_DETAIL.md`). |

### WS-02 Audit Logging Primitives

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-06 Handoff logging | DONE | TC-FR06-001 | PASS | CH-001 audit replay produced new entries (`audit/handoff.jsonl`, `audit/handoff_ms01_phase0.jsonl`). |
| FR-09 Command audit trail | DONE | TC-FR06-001 | PASS | `/status` `/clarify` `/approve` events recorded for CH-001 (`audit/commands.jsonl`). |

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
| FR-01 Project Manager coordination | DONE | TC-FR01-001, TC-FR01-002 | PASS | CH-001 execution confirmed PM orchestration and approvals (`artifacts/work/CH-001/run-04/manifest.json`). |
| FR-02 Status documentation maintained | DONE | TC-FR01-001 | PASS | Documentation reflects MS-01 refresh with validation evidence (`docs/PROJECT_OVERVIEW.md`). |
| FR-10 Approval capture | DONE | TC-FR10-001 | PASS | `/approve CH-001` event logged; QA report references approval chain. |

### WS-06 QA Policy Parser Stub

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-11 QA policy enforcement | PARTIAL | TC-FR11-001 | PASS | Parser validates schema; enforcement engine slated for Phase 1 WS-104. |

### WS-07 Demo Workflow Target

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-01 Orchestrated PM cycle | DONE | TC-FR01-002 | PASS | Demo bundle (`artifacts/phase0/demo/2025-11-02/`) documents PM→Designer→Implementer→Tester flow. |
| FR-06 Handoff logging completeness | DONE | TC-FR06-001 | PASS | Handoff logs regenerated with CH-001 metadata (`audit/handoff_ms01_phase0.jsonl`). |
| FR-09 Command audit trail | DONE | TC-FR09-001 | PASS | Demo commands + audit entries refreshed (`artifacts/phase0/demo/2025-11-02/commands.json`). |

### WS-08 Documentation Updates

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-02 Documentation currency | DONE | TC-FR01-001 | PASS | `PROJECT_OVERVIEW.md`, `PROJECT_DETAIL.md`, `VERSION_CONTROL.md` updated with CH-001 validation. |
| FR-10 Approval markers | DONE | TC-FR10-001 | PASS | CH-001 approval flow captured in docs and audit (`audit/commands.jsonl`). |

### WS-09 Discovery Foundations

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-38 Discovery pipeline artifacts | PLANNED | TC-FR38-001 | TODO | Discovery CLI will emit `analysis/system_manifest.yaml`, `analysis/change_zones.md`, `analysis/intent_map.md` per CR003. |
| FR-39 System Model Graph (YAML projections) | PLANNED | TC-FR39-001 | TODO | Design YAML schema for model graph; ensure repo-tracked projections remain canonical. |
| FR-41 Understanding coverage metrics | PLANNED | TC-FR41-001 | TODO | Define coverage/readiness calculations and store alongside discovery manifests. |

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
| WS-109 Implementer Micro-Loop & Retention | CHANGE IMPACTED | FR-04, FR-27, FR-29 | CR002 realigns micro-loop enforcement and retention; design updates slated in `docs/REQUIREMENTS_1_3.md` |
| WS-110 Loop Planning & Seed Generation | IN PROGRESS | FR-40 | Loop planning + seed flow (`design/MS-02_storyboard.md#stage-7`, `loop-plan.json`, `changes/CH-###/seed/REVIEW.md`) |

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
| FR-04 Implementation governance micro-loop | PARTIAL | TC-FR04-001, TC-FR04-002 (TODO) | PARTIAL | Implementer loop executes deterministically for core path; CR002 updates captured in `docs/REQUIREMENTS_1_3.md` require planner/executor refinements. |
| FR-27 Implementer run retention | PLANNED | TC-FR27-001 (TODO) | TODO | Retention policy must auto-purge successful runs after 48 h/2 GB and respect `.retain` markers. |
| FR-29 SpekKit-inspired micro-task loop | PLANNED | TC-FR29-001 (TODO) | TODO | Planner/executor/cleanup modules to reimplement SpekKit concepts without code reuse. |

### WS-110 Loop Planning & Seed Generation

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-40 Loop plan → seed packaging | IN PROGRESS | TC-FR40-001 (TODO) | PENDING | `codexa loop plan` captures execution scope; `codexa seed --from loop-plan` emits scoped bundles with manifests, baseline tests, and review digests (`design/MS-02_storyboard.md#stage-7`). |

---

## Phase 2 — Change Governance Loop

| Workstream | Status | Related Requirements | Evidence |
| --- | --- | --- | --- |
| WS-201 Requirements Intelligence | IN PROGRESS | FR-02, FR-15, FR-26, FR-37 | Conversational intake + curated requirements linked to discovery artifacts (`design/MS-02_storyboard.md#stage-5`) |
| WS-202 Impact Assessment & Evaluator | IN PROGRESS | FR-16 | Readiness heatmaps + follow-up orchestration feeding governance prompts (`design/MS-02_storyboard.md#stage-9`) |
| WS-203 Implementation Management | PLANNED | FR-21, FR-25, FR-31 | Implementation Manager brief (`IM_PROGRESS.md`) to be authored |
| WS-204 Governance & Multi-Gate Approvals | PLANNED | FR-10, FR-22, FR-34 | Governance Officer charter (`GOVERNANCE_REPORT.md`) pending |
| WS-205 Change Router & Orchestration | PLANNED | FR-01, FR-23 | Change router design notes (`docs/REQUIREMENTS_1_3.md`) |
| WS-206 Change Records & Audit Extensions | PLANNED | FR-06, FR-20, FR-26 | Audit schema expansion plan (`audit/`) to be drafted |
| WS-207 Interaction CLI Extensions | PLANNED | FR-24, FR-28 | `/impact`, `/trace`, `/df.*` CLI specs (planned) |

### WS-201 Requirements Intelligence

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-02 Status documentation (maturity summaries) | IN PROGRESS | TC-FR02-002 | TODO | Docs now include discovery/loop-plan context (`design/MS-02_storyboard.md` alignment pending final polish). |
| FR-15 Requirements Analyst agent | IN PROGRESS | TC-FR15-001 | TODO | Conversational intake + curated requirement outputs (`docs/requirements/curated/` prototypes) linked to discovery artifacts. |
| FR-26 Bidirectional change traceability | IN PROGRESS | TC-FR26-001 | TODO | Loop plan + seed metadata embed change IDs and discovery hashes. |
| FR-37 Requirement elaboration workflow | IN PROGRESS | TC-FR37-001 | TODO | Elaboration drafts incorporate discovery evidence before loop planning continues. |

### WS-202 Impact Assessment & Evaluator

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-16 Impact Assessor agent | IN PROGRESS | TC-FR16-001 | TODO | Conversational gap handling + readiness heatmaps drive governance prompts (see Stage 9 summary artifacts). |

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
| FR-06 Structured handoff logging (extended schema) | PLANNED | TC-FR06-002 | TODO | Append change, maturity, and discovery metadata to audit logs. |
| FR-20 RACI metadata propagation | PLANNED | TC-FR20-001 | TODO | Embed `raci_role` in audit logs and artifacts. |
| FR-26 Bidirectional change traceability | PLANNED | TC-FR26-001 | TODO | Ensure `CH-###` entries and FR/WS/TC artifacts cross-link with lifecycle state tracking. |

### WS-207 Interaction CLI Extensions

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-24 `/impact` and `/trace` commands | PLANNED | TC-FR24-001 | TODO | Support local and remote (Discord) contexts. |
| FR-28 `/df.clarify`, `/df.analyze`, `/df.checklist`, `codexa doctor` | PLANNED | TC-FR28-001 | TODO | Emit JSON logs under `artifacts/analyze/` for FR-06 ingestion. |

---

## Phase 3 — QA & Maturity Automation

| Workstream | Status | Related Requirements | Evidence |
| --- | --- | --- | --- |
| WS-301 QA Auditor & Traceability Gaps | PLANNED | FR-17 | Traceability gap workflow scoped in `docs/REQUIREMENTS_1_3.md` |
| WS-302 Test Synthesizer & Quality Depth | PLANNED | FR-05, FR-18, FR-19 | QA/Test agent briefs (`tests/`) to be generated |
| WS-303 QA Policy Engine Enhancements | PLANNED | FR-11 | Policy engine design update pending |
| WS-304 Maturity Metadata & Guides | PLANNED | FR-32, FR-33 | `PROJECT_METADATA.md`, `PROCESS_MATURITY_GUIDE.md` planned |
| WS-305 Maturity-Aware Agent Prompts | PLANNED | FR-35 | Prompt adaptation backlog item |
| WS-306 Maturity Metrics & Snapshots | PLANNED | FR-13, FR-30, FR-36, FR-41 | Metrics dashboard plan upcoming |

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
| FR-41 Understanding coverage & readiness metrics | PLANNED | TC-FR41-001 | TODO | Report % coverage of mapped components and readiness heatmaps sourced from discovery artifacts. |

---

## Overview by Requirement

| Requirement | Current Status | Validating Workstreams | Primary Tests / Evidence |
| --- | --- | --- | --- |
| FR-01 Project Manager agent coordination | PARTIAL | WS-01, WS-05, WS-07, WS-101, WS-205 | TC-FR01-001, TC-FR01-002, TC-FR01-003 (TODO), `artifacts/phase1/orchestration/run.log` |
| FR-02 Status documentation | PARTIAL | WS-01, WS-05, WS-08, WS-108, WS-201 | TC-FR01-001, TC-FR02-002 (TODO), `docs/PROJECT_OVERVIEW.md` |
| FR-03 Designer agent deliverables | PARTIAL | WS-101 | TC-FR03-001, `design/DESIGN_SPEC.md` |
| FR-04 Implementer branch + artifact discipline | PARTIAL | WS-101 | TC-FR04-001, `docs/IMPLEMENTATION_PLAN.md` |
| FR-05 Tester-owned QA artifacts | PARTIAL | WS-104, WS-302 | TC-FR05-001, TC-FR05-002 (TODO), `tests/TEST_PLAN.md` |
| FR-06 Handoff logging | PARTIAL | WS-02, WS-04, WS-07, WS-101, WS-206 | TC-FR06-001, TC-FR06-002 (TODO), `artifacts/phase0/demo/` with discovery metadata pending |
| FR-07 Concern lifecycle | PARTIAL | WS-03, WS-102 | TC-FR07-001, `pipelines/concern_tools.py` |
| FR-08 Discord bridge commands | PARTIAL | WS-04, WS-105 | TC-FR08-001, TC-FR08-002 (TODO), `artifacts/phase1/commands/` |
| FR-09 Command audit trail | PARTIAL | WS-02, WS-04, WS-05, WS-105 | TC-FR09-001, `audit/commands.jsonl` |
| FR-10 Approval governance | PARTIAL | WS-05, WS-08, WS-103, WS-108, WS-204 | TC-FR10-001, TC-FR10-002 (TODO), `artifacts/phase1/approvals/denied.txt` |
| FR-11 QA policy enforcement | PARTIAL | WS-06, WS-104, WS-303 | TC-FR11-001, TC-FR11-002 (TODO), TC-FR11-003 (TODO) |
| FR-12 GitOps workflow controls | PLANNED | Future phase | TC-FR12-001 (TODO) |
| FR-13 Status snapshots | PLANNED | WS-106, WS-306 | TC-FR13-001 (TODO), TC-FR13-002 (TODO) |
| FR-14 Rollback & pause controls | PLANNED | WS-107 | TC-FR14-001 (TODO) |
| FR-15 Requirements Analyst agent | IN PROGRESS | WS-201 | TC-FR15-001 (TODO), curated intake pipeline (`design/MS-02_storyboard.md#stage-5`) |
| FR-16 Impact Assessor agent | IN PROGRESS | WS-202 | TC-FR16-001 (TODO), readiness heatmap governance prompts |
| FR-17 QA Auditor agent | PLANNED | WS-301 | TC-FR17-001 (TODO) |
| FR-18 Test Synthesizer agent | PLANNED | WS-302 | TC-FR18-001 (TODO) |
| FR-19 Test Quality Assessor | PLANNED | WS-302 | TC-FR19-001 (TODO) |
| FR-20 RACI metadata propagation | PLANNED | WS-206 | TC-FR20-001 (TODO) |
| FR-21 Implementation Manager agent | PLANNED | WS-203 | TC-FR21-001 (TODO) |
| FR-22 Governance Officer agent | PLANNED | WS-204 | TC-FR22-001 (TODO) |
| FR-23 Automated orchestration triggers | PLANNED | WS-205 | TC-FR23-001 (TODO) |
| FR-24 `/impact` and `/trace` commands | PLANNED | WS-207 | TC-FR24-001 (TODO) |
| FR-25 Change workspace management | PLANNED | WS-203 | TC-FR25-001 (TODO), `changes/CH-###/` template plan |
| FR-26 Bidirectional change traceability | IN PROGRESS | WS-201, WS-206 | TC-FR26-001 (TODO); loop-plan metadata threads discovery ⇄ change ⇄ execution |
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
| FR-37 Requirement elaboration workflow | IN PROGRESS | WS-201 | TC-FR37-001 (TODO); elaborations now embed discovery evidence before loop planning |
| FR-38 Discovery pipeline artifacts | IN PROGRESS | WS-09 | TC-FR38-001 (TODO); telemetry + iteration log updates (`docs/discovery/config.yaml`, `docs/status/iteration_log.md`) |
| FR-39 System Model Graph (YAML projections) | IN PROGRESS | WS-09 | TC-FR39-001 (TODO); projections now include iteration/follow-up metadata (`analysis/system_model/`) |
| FR-40 Loop plan → seed packaging | IN PROGRESS | WS-110 | TC-FR40-001 (TODO); loop plan + `codexa seed --from loop-plan` flow (`design/MS-02_storyboard.md#stage-7`) |
| FR-41 Understanding coverage & readiness metrics | IN PROGRESS | WS-09, WS-306 | TC-FR41-001 (TODO); coverage surfaced via `/status` + governance summary (`design/MS-02_storyboard.md#stage-9`) |
