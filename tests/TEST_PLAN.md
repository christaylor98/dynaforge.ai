# Test Plan — Phase 1

## Scenario — Concern Lifecycle Integration
Implement concern lifecycle mirroring, lifecycle commands, and QA enforcement gates.

## Objectives
- Validate concern logging mirrors into Markdown summaries.
- Exercise interaction stub lifecycle commands for deterministic responses.
- Confirm QA policy enforcement blocks promotions on open concerns.

## Test Strategy
- Automated unit coverage for audit primitives, concern lifecycle utilities, policy parsing, and interaction commands.
- Automated integration coverage across the agent orchestration loop to ensure artifacts and audit records align with requirements.
- Targeted manual validation to demonstrate lifecycle command transcripts, QA enforcement behaviour, and operational pause/resume controls as they land.

## Test Environments
- Local developer workstation (Python 3.11+).
- Continuous integration pipeline (TBD) with audit artifact capture.

## Entry Criteria
- Phase 1 design and implementation plans approved by human reviewer.
- Concern lifecycle helpers available in the codebase.
- Interaction stub expanded with lifecycle commands.

## Exit Criteria
- All critical tests passing with evidence stored under `artifacts/phase1/`.
- No unresolved high/critical concerns in `audit/concerns.jsonl`.
- Approval marker recorded in documentation.

## Test Catalogue

Each test case ID maps to one or more functional requirements (FR-xx). Automated tests reference the concrete Python test function or module that executes the coverage.

### Automated Coverage (Executed)

| ID | Requirement(s) | Type | Description | Evidence Artifact |
| --- | --- | --- | --- | --- |
| TC-FR01-001 | FR-01, FR-02 | Integration | `ProjectManager.run` refreshes overview/detail docs and records handoff entry. | `tests/test_agents_workflow.py::ProjectManagerIntegrationTest` |
| TC-FR01-002 | FR-01 | Integration | Orchestrator executes PM→Designer→Implementer→Tester sequence and writes summary bundle. | `tests/test_agents_workflow.py::Phase1OrchestratorIntegrationTest` |
| TC-FR03-001 | FR-03 | Integration | Designer generates deterministic spec linked to brief and logs handoff. | `tests/test_agents_workflow.py::DesignerIntegrationTest` |
| TC-FR04-001 | FR-04 | Integration | Implementer produces execution plan referencing design artifacts and handoff metadata. | `tests/test_agents_workflow.py::ImplementerIntegrationTest` |
| TC-FR05-001 | FR-05 | Integration | Tester prepares phase test assets and logs handoff to human reviewer. | `tests/test_agents_workflow.py::TesterIntegrationTest` |
| TC-FR06-001 | FR-06 | Unit | Audit logger writes schema-compliant handoff entries with coverage assertions. | `tests/test_logger.py` |
| TC-FR07-001 | FR-07 | Unit | Concern tools raise, update, resolve, and sync Markdown sections from JSONL source. | `tests/test_concern_tools.py` |
| TC-FR08-001 | FR-08 | Unit | Interaction stub handles lifecycle commands (`/status`, `/clarify`, `/ack`, `/resolve`, `/assign`, `/pause`, `/resume`, `/promote`). | `tests/test_interaction_stub.py` |
| TC-FR09-001 | FR-09 | Unit | Interaction stub command handlers emit structured audit entries. | `tests/test_interaction_stub.py` |
| TC-FR10-001 | FR-10 | Unit | Orchestrator enforces approval marker presence before run proceeds. | `tests/test_phase1_orchestrator.py` |
| TC-FR11-001 | FR-11 | Unit | Policy parser loads, validates, and summarises QA policy schema. | `tests/test_policy_parser.py` |

### Manual / Planned Coverage (Pending)

| ID | Requirement(s) | Type | Description | Planned Evidence |
| --- | --- | --- | --- | --- |
| TC-FR08-002 | FR-08, FR-09 | Manual Integration | Replay lifecycle commands via stub/CLI and capture corresponding audit transcripts. | `artifacts/phase1/commands/` (to be updated) |
| TC-FR11-002 | FR-11 | Integration | Execute QA enforcement CLI against passing/failing fixtures to raise concerns automatically. | `tests/test_policy_parser.py` extension + `audit/concerns.jsonl` |
| TC-FR13-001 | FR-13 | Integration | Generate status snapshot (`status.json` or Markdown digest) and reconcile with audit/doc state. | `artifacts/phase1/status/` |
| TC-FR14-001 | FR-14 | Integration | Validate pause/resume/rollback controls with audit logging of state changes. | `artifacts/phase1/rollback/` |
| TC-FR12-001 | FR-12 | Integration | Demonstrate GitOps safeguards (protected branches, tagging) via scripted workflow. | CI pipeline evidence (Phase 2) |

_Maintained by Tester agent — updated 2025-10-29._
