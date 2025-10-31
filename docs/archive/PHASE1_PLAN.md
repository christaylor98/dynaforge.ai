# Phase 1 Plan — Core Agent Loop

## 1. Purpose & Scope
Deliver the first fully coordinated multi-agent execution loop on top of the Phase 0 foundation. Phase 1 focuses on operationalizing the core agents (Project Manager, Designer, Implementer, Tester), enforcing concern and approval workflows, expanding the interaction bridge, and wiring QA policy enforcement so humans can govern real deliverables with evidence.

## Reference Documents
- `docs/WORKFLOW.md` — operational workflow and handoff expectations.
- `docs/PROMPT_GUIDE.md` — cross-agent prompting conventions.
- `docs/project-qa.md` — QA entry/exit criteria and policy thresholds.
- `docs/OVERLORD_WORKFLOW.md` — lifecycle view across agents and humans.
- `.codex/context/architecture-summary.md` — architectural principles and guardrails.
- `docs/REQUIREMENTS.md` — functional requirements FR-01 through FR-14.
- `tests/TEST_PLAN.md` — tester-owned validation scope and methodology.
- `docs/ARCHITECTURE.md` — detailed design of modules and interactions.

### Phase Goals
- Enable an automated PM → Designer → Implementer → Tester → Human loop driven by handoffs and approvals.
- Persist concern and command events end-to-end, including Markdown mirroring and alert hooks.
- Evaluate QA policy thresholds before promotions and surface failures as actionable feedback.
- Extend the interaction stub to cover the operational Discord commands required by FR-08.
- Produce status snapshots and rollback controls aligned with Phase 1 functional targets.

## 2. Workstreams & Tasks

| ID | Workstream | Key Tasks | Primary Owner | Dependencies | Validation Anchor |
| -- | ---------- | --------- | ------------- | ------------ | ----------------- |
| WS-101 | Multi-Agent Orchestration | Implement Designer/Implementer/Tester agent modules; add orchestration script that sequences handoffs, reads requirements, updates docs, and emits logger events. | Implementer | Phase 0 foundation | Dry-run script produces complete loop artifacts captured under `artifacts/phase1/orchestration`. |
| WS-102 | Concern Lifecycle | Extend `audit` helpers to write `concerns.jsonl`, mirror entries into `docs/PROJECT_DETAIL.md`, and support resolution updates; document concern playbook. | PM Agent | WS-101 | Sample concern raised and resolved; Markdown + JSON entries reconciled. |
| WS-103 | Human Approval Gates | Add approval prompts and enforcement in PM + orchestration scripts; embed approval markers into docs; block progression without approvals. | PM Agent | WS-101 | Handoff halted until approval marker added; audit log captures approval metadata. |
| WS-104 | QA Policy Enforcement | Expand `pipelines/policy_parser.py` into enforcement engine that ingests test results, evaluates thresholds, raises concerns on failure, and exposes CLI entrypoint. | Tester | WS-101 | Unit & integration tests verifying policy pass/fail paths; failure triggers concern automatically. |
| WS-105 | Interaction Bridge Expansion | Update interaction stub to handle `/ack`, `/resolve`, `/assign`, `/pause`, `/resume`, `/promote`; ensure command logging and agent routing. | Implementer + Tester | WS-101, WS-102 | Manual command replay shows expected responses and audit entries in `audit/commands.jsonl`. |
| WS-106 | Status Snapshots & Observability | Generate `status.json` (or Markdown digest) summarizing phase progress, open concerns, QA posture; integrate into PM loop and `make` targets. | PM Agent | WS-101–WS-105 | Snapshot file generated after demo run; values match audit/doc state. |
| WS-107 | Rollback & Pause Controls | Provide scripts or make targets to pause/resume workflows, revert last approved change, and document operator procedure. | Implementer | WS-101, WS-103 | `make pause`/`make resume` or equivalent commands validated; audit captures pause events. |
| WS-108 | Demo & Documentation | Deliver `make phase1-demo` executing full loop, collecting artifacts (`artifacts/phase1/**`), and update documentation (`PROJECT_OVERVIEW`, `PROJECT_DETAIL`, new approvals). | PM Agent + Tester | WS-101–WS-107 | Demo run recorded with matching audit logs; docs show Phase 1 readiness with approval line. |

## 3. Validation Plan

| Workstream | Verification Steps | Owner | Evidence Artifact |
| ---------- | ------------------ | ----- | ----------------- |
| WS-101 | Run orchestration script twice; verify idempotent outputs and complete handoff recordings. | Tester | `artifacts/phase1/orchestration/run.log` |
| WS-102 | Raise, update, and resolve a concern; confirm JSONL ↔ Markdown sync and notification hook execution. | Tester | `audit/concerns.jsonl`, `docs/PROJECT_DETAIL.md` excerpt |
| WS-103 | Attempt progression without approval marker; ensure system blocks and logs violation. | Tester | `artifacts/phase1/approvals/denied.txt` |
| WS-104 | Execute enforcement CLI with passing and failing test result fixtures; observe concern creation on failure. | Tester | `tests/TEST_RESULTS_DETAIL.md` updates |
| WS-105 | Replay each supported command via stub; confirm command log entries with correct routing metadata. | Tester | `audit/commands.jsonl` filtered report |
| WS-106 | Inspect generated `status.json`; cross-check against audit counts and docs for accuracy. | Human Reviewer | `artifacts/phase1/status/status.json` |
| WS-107 | Trigger pause/resume and rollback flows; ensure audit trail and state restoration succeed. | Tester | `artifacts/phase1/rollback/rollback.log` |
| WS-108 | Execute `make phase1-demo`; review artifact bundle and documentation diff for completeness. | Human Reviewer | `QA_REPORT.md` (Phase 1) |

## 4. Exit Criteria
- Orchestration run executes core agent loop, with logged handoffs, approvals, concerns, and QA enforcement outcomes.
- Concern lifecycle demonstrably mirrors JSONL entries into Markdown and supports resolution tracking.
- Approval gates prevent progression until human markers are present and logged.
- QA policy engine blocks promotions when thresholds fail and raises concerns automatically.
- Interaction bridge handles all Phase 1 command set with audit coverage.
- Status snapshot reflects live project metrics and matches audit sources.
- Pause/resume and rollback utilities work and are documented for operators.
- Documentation updated with Phase 1 scope, approvals, and operator checklists; artifacts stored under `artifacts/phase1/`.

## 5. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Approval gating becomes brittle and blocks legitimate workflows. | Medium | High | Provide override procedure with explicit audit entry; add regression tests for approval detection. |
| Concern mirroring between JSONL and Markdown drifts over time. | Medium | Medium | Centralize concern rendering helper; add nightly reconciliation check in Phase 2. |
| QA enforcement generates noisy false positives. | Medium | Medium | Parameterize thresholds via `QA_POLICY.yaml`; include dry-run mode and clear diagnostics. |
| Expanded command set complicates interaction stub maintenance. | Low | Medium | Document command handler contracts; add unit tests per command to ensure determinism. |
| Rollback scripts inadvertently lose data. | Low | High | Implement dry-run preview; log affected files and require human confirmation before destructive actions. |

## 6. Timeline & Checkpoints
- **Week 1**: Complete WS-101, WS-102 foundations; interaction stub updates drafted (WS-105).
- **Week 2**: Land approval gating (WS-103), QA enforcement (WS-104), and status snapshot wiring (WS-106).
- **Week 3**: Finalize pause/rollback tooling (WS-107), polish demo & documentation (WS-108), capture validation artifacts.

## 7. Approvals & Governance
- Human reviewer must sign off on this Phase 1 plan (`docs/PROJECT_OVERVIEW.md` entry) before implementation.
- Human reviewer validates Phase 1 completion via `/promote phase1`, tagging release `v0.2.0-phase1` and archiving artifacts.
- All Phase 1 activities logged in `audit/handoff_*.json`, `audit/concerns.jsonl`, and `audit/commands.jsonl`; approval markers embedded in relevant Markdown.

## 8. Current Status
- 🟢 Phase 1 plan approved by human reviewer (2025-10-29) and orchestration skeleton delivered (`make phase1-demo`).
