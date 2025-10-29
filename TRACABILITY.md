# Traceability Matrix

_Last updated: 2025-10-29 — maintained by Codex agent._

## Legend
- Workstream status: `DONE` (delivered), `IN PROGRESS` (currently active), `PLANNED` (not started).
- Requirement status: `DONE` (implemented with evidence), `PARTIAL` (in progress or partially validated), `IN PROGRESS` (active work), `PLANNED` (not yet implemented).
- Test status: `PASS` (evidence recorded), `PENDING` (test exists but not yet executed or captured), `TODO` (test not implemented).

---

## Phase 0 — Foundation

| Workstream | Status | Related Requirements | Evidence |
| --- | --- | --- | --- |
| WS-01 Repository Skeleton | DONE | FR-01, FR-02 | Repository structure and docs seeded (`docs/PHASE0_PLAN.md`) |
| WS-02 Audit Logging Primitives | DONE | FR-06, FR-09 | JSONL logger and sample artifacts (`audit/logger.py`, `audit/sample_handoff.jsonl`) |
| WS-03 Concern API & Schema Docs | PARTIAL | FR-07 | Concern helpers exported; schema documented in workflow guide (`docs/WORKFLOW.md`) |
| WS-04 Interaction Stub | DONE | FR-08, FR-09 | CLI stub with `/status` and `/clarify` wired to logging (`pipelines/interaction_stub.py`) |
| WS-05 Project Manager Skeleton | DONE | FR-01, FR-02 | PM agent updates docs and logs handoffs (`agents/project_manager.py`) |
| WS-06 QA Policy Parser Stub | PARTIAL | FR-11 | Parser stub plus unit tests (TC-FR11-001, `pipelines/policy_parser.py`) |
| WS-07 Demo Workflow Target | DONE | FR-01, FR-06, FR-09 | `make demo` artifacts (`artifacts/phase0/demo/`) |
| WS-08 Documentation Updates | DONE | FR-02, FR-10 | Docs refreshed with approval markers (`docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_DETAIL.md`) |

### WS-01 Repository Skeleton

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-01 Project Manager agent scaffolding | PARTIAL | TC-FR01-001 | PASS | Baseline directories and docs enable PM agent; integration test confirms doc refresh and audit handoff wiring. |
| FR-02 Status documentation maintained | DONE | TC-FR01-001 | PASS | `docs/PROJECT_OVERVIEW.md` and `docs/PROJECT_DETAIL.md` generation validated via integration test. |

### WS-02 Audit Logging Primitives

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-06 Handoff logging | DONE | TC-FR06-001 | PASS | JSONL writer validated; coverage recorded under `artifacts/phase0/trace/coverage_summary.txt`. |
| FR-09 Command audit trail | DONE | TC-FR06-001 | PASS | Logging helpers leveraged by interaction stub to capture commands. |

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
| FR-02 Status documentation maintained | DONE | TC-FR01-001 | PASS | Documents auto-refreshed by `ProjectManager.run`; integration test validates output structure. |
| FR-10 Approval capture | PARTIAL | TC-FR10-001 | PASS | Approval markers defined; enforcement completed under Phase 1 WS-103 with passing unit test. |

### WS-06 QA Policy Parser Stub

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-11 QA policy enforcement | PARTIAL | TC-FR11-001 | PASS | Parser validates schema; enforcement engine slated for Phase 1 WS-104. |

### WS-07 Demo Workflow Target

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-01 Orchestrated PM cycle | PARTIAL | TC-FR01-002 | PASS | Demo exercises PM + logging; integration test executes orchestrator and verifies artifact bundle. |
| FR-06 Handoff logging completeness | DONE | TC-FR06-001 | PASS | Demo run captures handoff artifacts in `artifacts/phase0/demo/`. |
| FR-09 Command audit trail | DONE | TC-FR09-001 | PASS | Demo ensures command log appended during interaction stub runs. |

### WS-08 Documentation Updates

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-02 Documentation currency | DONE | TC-FR01-001 | PASS | Overview and detail docs aligned with Phase 0 scope and regenerated in integration test. |
| FR-10 Approval markers | PARTIAL | TC-FR10-001 | PASS | Approval checklist established; enforcement validated in Phase 1. |

---

## Phase 1 — Core Agent Loop

| Workstream | Status | Related Requirements | Evidence |
| --- | --- | --- | --- |
| WS-101 Multi-Agent Orchestration | DONE | FR-01, FR-04, FR-06 | Orchestrator loop artifacts (`artifacts/phase1/orchestration/run.log`) |
| WS-102 Concern Lifecycle | IN PROGRESS | FR-07 | Concern toolkit foundations (`pipelines/concern_tools.py`) |
| WS-103 Human Approval Gates | DONE | FR-10 | Approval enforcement tests (TC-FR10-001, `artifacts/phase1/approvals/denied.txt`) |
| WS-104 QA Policy Enforcement | PLANNED | FR-11 | Pending implementation (see `PROGRESS.md`) |
| WS-105 Interaction Bridge Expansion | DONE | FR-08, FR-09 | Extended commands + audit logs (`pipelines/interaction_stub.py`, `artifacts/phase1/commands/`) |
| WS-106 Status Snapshots & Observability | PLANNED | FR-13 | Pending orchestration hook |
| WS-107 Rollback & Pause Controls | PLANNED | FR-14 | Scripts not yet implemented |
| WS-108 Demo & Documentation | IN PROGRESS | FR-02, FR-10 | Documentation refresh pending completion of WS-104–WS-107 |

### WS-101 Multi-Agent Orchestration

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-01 Project Manager coordinates agents | DONE | TC-FR01-002 | PASS | Orchestrator sequences PM→Designer→Implementer→Tester with audit handoffs. |
| FR-04 Implementer alignment with design | PARTIAL | TC-FR04-001 | PASS | Implementer hooks scaffolded; full enforcement of branch policy outstanding. |
| FR-06 Handoff logging (loop) | DONE | TC-FR06-001 | PASS | Run logs in `artifacts/phase1/orchestration/run.json` show full handoff trail. |

### WS-102 Concern Lifecycle

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-07 Concern lifecycle automation | PARTIAL | TC-FR07-001 | PASS | Unit test raises, updates, resolves concerns and mirrors Markdown; integration demo still pending. |

### WS-103 Human Approval Gates

| Requirement | Requirement Status | Tests | Test Status | Notes |
| --- | --- | --- | --- | --- |
| FR-10 Approval enforcement | DONE | TC-FR10-001 | PASS | Orchestrator blocks progression without inline approval marker; denial log stored at `artifacts/phase1/approvals/denied.txt`. |

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

---

## Overview by Requirement

| Requirement | Current Status | Validating Workstreams | Primary Tests / Evidence |
| --- | --- | --- | --- |
| FR-01 Project Manager agent coordination | PARTIAL | WS-01, WS-05, WS-07, WS-101 | TC-FR01-001, TC-FR01-002, `artifacts/phase1/orchestration/run.log` |
| FR-02 Status documentation | DONE | WS-01, WS-05, WS-08, WS-108 | TC-FR01-001, `docs/PROJECT_OVERVIEW.md` |
| FR-03 Designer agent deliverables | PARTIAL | WS-101 | TC-FR03-001, `design/DESIGN_SPEC.md` |
| FR-04 Implementer branch + artifact discipline | PARTIAL | WS-101 | TC-FR04-001, `docs/IMPLEMENTATION_PLAN.md` |
| FR-05 Tester-owned QA artifacts | PARTIAL | WS-104 | TC-FR05-001, `tests/TEST_PLAN.md` |
| FR-06 Handoff logging | DONE | WS-02, WS-04, WS-07, WS-101 | TC-FR06-001, `artifacts/phase0/demo/` |
| FR-07 Concern lifecycle | PARTIAL | WS-03, WS-102 | TC-FR07-001, `pipelines/concern_tools.py` |
| FR-08 Discord bridge commands | PARTIAL | WS-04, WS-105 | TC-FR08-001, TC-FR08-002 (TODO), `artifacts/phase1/commands/` |
| FR-09 Command audit trail | DONE | WS-02, WS-04, WS-05, WS-105 | TC-FR09-001, `audit/commands.jsonl` |
| FR-10 Approval governance | PARTIAL | WS-05, WS-08, WS-103, WS-108 | TC-FR10-001, `artifacts/phase1/approvals/denied.txt` |
| FR-11 QA policy enforcement | PARTIAL | WS-06, WS-104 | TC-FR11-001, TC-FR11-002 (TODO) |
| FR-12 GitOps workflow controls | PLANNED | Future phase | TC-FR12-001 (TODO) |
| FR-13 Status snapshots | PLANNED | WS-106 | TC-FR13-001 (TODO) |
| FR-14 Rollback & pause controls | PLANNED | WS-107 | TC-FR14-001 (TODO) |
