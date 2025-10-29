# Phase 0 Plan — Foundation

## 1. Purpose & Scope
Establish the minimal but complete skeleton of the Code Overlord framework so subsequent phases can iterate safely. Phase 0 focuses on repository structure, audit/logging primitives, initial agent stubs, and a usable interaction mock with deterministic validation.

### Phase Goals
- Provide a consistent project layout (`docs/`, `design/`, `tests/`, `audit/`, `pipelines/`, etc.).
- Deliver baseline logging and handoff artifacts to prove auditability.
- Expose a working interaction stub (Discord CLI mock) supporting `/status` and `/clarify`.
- Demonstrate a simple end-to-end loop via `make demo`, capturing artifacts and logs.
- Document everything needed for Human approval of the foundation.

## 2. Workstreams & Tasks

| ID | Workstream | Key Tasks | Primary Owner | Dependencies | Validation Anchor |
| -- | ---------- | --------- | ------------- | ------------ | ----------------- |
| WS-01 | Repository Skeleton | Create directories; seed placeholder markdown (`docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_DETAIL.md`, `tests/TEST_PLAN.md`); add `.gitkeep` where needed. | PM Agent | None | `tree` output matches spec; placeholders tracked in Git. |
| WS-02 | Audit Logging Primitives | Implement `audit/logger.py` with JSONL writer; define handoff & concern schemas in code and docstring. | PM Agent (delegating to Implementer) | WS-01 | Unit test writing/reading JSON entries; sample log file committed to `audit/sample_handoff.jsonl`. |
| WS-03 | Concern API & Schema Docs | Provide `log_handoff()`/`log_concern()` helper functions; document schema in `docs/WORKFLOW.md` addendum. | Implementer | WS-02 | Helper functions produce schema-compliant entries inspected via `jq`. |
| WS-04 | Interaction Stub | Build lightweight CLI/Discord mock (`pipelines/interaction_stub.py`) that accepts `/status` & `/clarify` and prints deterministic responses; wire to logger. | Implementer + Tester | WS-02, WS-03 | Manual run `python pipelines/interaction_stub.py /status` shows expected JSON + log entry. |
| WS-05 | Project Manager Skeleton | Create `agents/project_manager.py` with ability to read requirements, update doc placeholders, and call logging helpers. | PM Agent | WS-01–WS-04 | Dry-run script populates summary docs; diff captured for review. |
| WS-06 | QA Policy Parser Stub | Implement `pipelines/policy_parser.py` that loads `QA_POLICY.yaml`, validates schema, and prints summary. | Tester | WS-01 | Unit test with sample policy; failure cases raise explicit errors. |
| WS-07 | Demo Workflow Target | Add `Makefile` targets: `make demo`, `make audit`, `make clean`. Demo should execute PM skeleton, interaction stub, and generate logs. | PM Agent + Implementer | WS-01–WS-06 | Running `make demo` produces artifacts (docs updated, audit logs, terminal summary) verified by Tester. |
| WS-08 | Documentation Updates | Update `docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_DETAIL.md`, `docs/OVERLORD_WORKFLOW.md` with Phase 0 progress and instructions. | PM Agent | WS-01–WS-07 | Human reviewer approves documentation (`✅ Approved by Human <date>`). |

## 3. Validation Plan

| Workstream | Verification Steps | Owner | Evidence Artifact |
| ---------- | ------------------ | ----- | ----------------- |
| WS-01 | Run `tree` against repo; ensure required directories exist; verify placeholders in Git diff. | Tester | `artifacts/phase0/tree.txt` |
| WS-02/03 | Execute unit tests (`pytest tests/test_logger.py`); inspect `audit/sample_handoff.jsonl` for schema compliance. | Tester | `tests/TEST_RESULTS_DETAIL.md` excerpt |
| WS-04 | Manual invocation of stub commands (`/status`, `/clarify`) logged with timestamps; cross-check `commands.jsonl`. | Tester | `artifacts/phase0/interaction_demo.log` |
| WS-05 | PM skeleton run updates docs; reviewer inspects diff to confirm structured sections populated. | Human Reviewer | Git diff attached to review log |
| WS-06 | Provide positive/negative YAML samples; ensure parser errors are descriptive. | Tester | `tests/TEST_RESULTS.md` |
| WS-07 | Run `make demo` end-to-end; ensure logs, docs, and demo output align; rerun to confirm idempotence. | Tester | `QA_REPORT.md` (Phase 0) |
| WS-08 | Human reviewer reads updated docs and adds approval annotation; confirm concern list empty. | Human Reviewer | `docs/PROJECT_OVERVIEW.md` annotation |

## 4. Exit Criteria
- All Phase 0 workstreams completed with evidence artifacts stored under `artifacts/phase0/`.
- `make demo` executes without errors and produces reproducible outputs on two consecutive runs.
- Audit logs exist for at least one handoff and one concern, both schema-compliant and timestamped.
- `commands.jsonl` captures at least one `/status` and `/clarify` invocation.
- Documentation updated with Phase 0 status, including explicit human approval lines.
- Open concern count is zero; any raised concerns are closed with resolution notes.

## 5. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Logging schema drifts before downstream agents consume it. | Medium | High | Freeze schema in doc + unit tests; add CI check to validate JSON entries. |
| Interaction stub diverges from future Discord/CLI interface. | Medium | Medium | Centralize command parsing; document adapter contract; reuse in Phase 1. |
| Demo target becomes brittle as repo grows. | Low | Medium | Keep demo deterministic; document cleanup expectations; enforce idempotence checks. |
| Documentation lacks clarity for human approval. | Medium | High | Peer review within agents; provide checklist in `PROJECT_DETAIL.md`. |

## 6. Timeline & Checkpoints
- **Day 1–2**: WS-01, WS-02, WS-03 complete; initial audit/logging validated.
- **Day 3**: WS-04, WS-05 functional; first end-to-end dry run captured.
- **Day 4**: WS-06 integration; QA policy parsing tests written.
- **Day 5**: WS-07, WS-08 finalized; `make demo` validated; human approval obtained.

## 7. Approvals & Governance
- Human reviewer must sign off on this Phase 0 plan before execution (`docs/PROJECT_OVERVIEW.md` entry).
- Upon completion, human reviewer validates Phase 0 via `/promote phase0` (or documented equivalent), triggering tag `v0.1.0-phase0`.
- All steps logged through `audit/handoff_*.json` and `audit/commands.jsonl` to maintain traceability.

