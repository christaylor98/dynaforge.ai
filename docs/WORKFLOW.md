# Codexa Build Workflow — Milestone 1

## 1. Purpose
- Provide the single source of truth for how we deliver MS-01 (POC Spike) from request through acceptance.
- Align human and agent collaboration so every increment is observable, reversible, and reviewable.
- Anchor delivery on the SpekKit-inspired micro flow defined in FR-29 while fitting the Codexa repo layout and audit discipline.

## 2. MS-01 Scope & Outcomes
- Objective: demo the PM → Designer → Implementer → Tester agent loop with human-visible logging, approvals, and packaged demo collateral.
- Success looks like a human running `make demo` (or equivalent) and seeing a full cycle with audit evidence, status commands, and documentation that explains the loop.
- Out of scope for this milestone: advanced governance automation, maturity scoring, GitOps merges; track them for later phases but do not block MS-01.

## 3. Guiding Principles
- Work in micro increments that finish the SpekKit flow inside one change workspace (`changes/CH-###`).
- Capture proof (logs, diffs, test results) as we go; promotion requires evidence, not vibes.
- Keep the human in the loop for framing and approvals, but let agents execute repeatable tasks.
- Prefer deterministic behaviour (seeded planners, scripted commands) so replays are possible.
- Update documentation and traceability as part of the flow, not after the fact.

## 4. SpekKit Micro Flow (FR-29)
Our delivery loop adapts the SpekKit cadence into six deterministic stages. Every change request iterates them top-to-bottom; if a stage fails we fix it before advancing.

| Stage | Purpose | Primary Owner(s) | Key Artifacts | Exit Criteria |
| --- | --- | --- | --- | --- |
| **Frame** | Understand the change request, scope the slice, confirm acceptance tests. | Human PM + PM agent | `changes/CH-###/brief.md`, `/status` note | Stakeholder agrees on scope + explicit accept criteria. |
| **Spec** | Decompose work into deterministic micro-tasks. | PM agent + Designer agent | `changes/CH-###/tasks.md`, `planner_config.json` | Approved task list seeded and checked into repo. |
| **Execute** | Apply code/doc/test updates task-by-task, logging evidence. | Implementer agent | `artifacts/work/CH-###/run-*/`, diffs, audit logs | All tasks complete, no failing assertions, audit events recorded. |
| **Validate** | Run automated tests, synthesize QA notes, surface concerns. | Tester agent | `tests/results/CH-###.json`, `QA_REPORT.md`, audit entries | Required tests pass or concern logged; QA sign-off ready. |
| **Package** | Summarize impact, update docs, prep demo collateral. | PM agent + Human | `changes/CH-###/impact.md`, `docs/PROJECT_OVERVIEW.md`, demo assets | Stakeholder review packet ready, documentation updated. |
| **Cleanup** | Apply retention policy, close workspace, tag milestone artifacts. | Implementer agent + Governance | `audit/retention.jsonl`, closed `changes/` workspace | Evidence archived, workspace status updated, concern queue clear. |

### Flow Expectations
- Each stage emits events via `AuditLogger`, producing `audit/handoff.jsonl`, `audit/concerns.jsonl`, and run-specific logs.
- Stage owners may loop locally (e.g., Execute ↔ Validate) but must not promote without re-running Validate and Package.
- The PM agent orchestrates movement between stages and records stage status in `PROGRESS.md`.

## 5. Iteration Rhythm
- **Kickoff**: Human PM selects highest-priority MS-01 backlog item and opens/refreshes `changes/CH-###` workspace with Frame deliverables.
- **Daily Flow**: At least one SpekKit cycle completes per day; unfinished stages roll forward with explicit blockers noted in `audit/concerns.jsonl`.
- **Sync Points**: Human reviews at end of Spec, after Validate, and during Package. Approvals recorded via `/approve CH-###` command.
- **Demo Fridays**: Package stage outputs weekly demo updates stored under `artifacts/phase1/demo/Week-##/`.

## 6. Role & Responsibility Matrix
| Role | Key Responsibilities in MS-01 | Hand-off Notes |
| --- | --- | --- |
| Human PM | Prioritize backlog, approve Frame/Spec, evaluate Package, decide promotion. | Uses `/status`, `/clarify`, and `/approve` to control flow. |
| PM Agent | Drive backlog intake, coordinate agents, maintain `PROGRESS.md`. | Receives human approvals, notifies Designer/Implementer. |
| Designer Agent | Convert requests into structured tasks and design notes. | Must store decisions in `design/DESIGN_SPEC.md` segments. |
| Implementer Agent | Execute tasks deterministically, generate diffs, call tests. | Logs each task completion with `{task_id, files_touched}`. |
| Tester Agent | Run declared test commands, update QA artifacts, raise concerns. | Blocks promotion until required evidence recorded. |
| Governance / Retention | Ensure cleanup stage respects retention policy. | Monitors `audit/retention.jsonl` and concern resolution. |

## 7. Evidence & Artifacts
- `audit/` JSONL files capture handoffs, commands, concerns, retention actions.
- `artifacts/work/CH-###/run-*/` holds run summaries, deterministic seeds, and task evidence.
- `changes/CH-###/impact.md` narrates scope, implementation notes, and verification.
- `tests/results/CH-###.json` (or similar) records automated test outcomes with timestamps.
- `docs/PROJECT_OVERVIEW.md` and `docs/IMPLEMENTATION_PLAN.md` updated whenever Package stage completes.

## 8. Testing & QA Strategy (MS-01 Focus)
- **Unit Tests** (`pytest`): cover new utilities and agent helpers touched during Execute.
- **Integration Harness** (`make demo` / scripted run): must replay PM→Designer→Implementer→Tester chain twice with identical audit output.
- **Manual Smoke**: Human triggers `/status`, `/clarify`, `/approve`, verifying responses and audit entries.
- **Regression Snapshot**: Rerun Execute+Validate with the same seed; diffs must match or raise a concern.

## 9. Approval & Promotion Gates
- Execute cannot start without human ✅ on Frame+Spec artifacts.
- Validate must pass all required tests or document waivers in `QA_REPORT.md` before Package.
- Package requires human ✅; once approved, PM agent tags milestone progress in `PROGRESS.md` and updates Milestone dashboard (`TRACEABILITY.md` MS-01 row).
- Cleanup closes the change workspace and lists evidence references in `PROGRESS.md` before the next backlog item starts.

## 10. Progress Tracking & Communication
- `PROGRESS.md` reflects current stage per change request plus aggregated milestone stats (coverage %, reproducibility %, open concerns).
- Daily digest posted to Discord `#build-status` summarizing completed stages and blockers.
- Weekly milestone status appended to `docs/STATUS_REPORT.md` referencing MS-01 readiness.

## 11. Immediate Next Steps
- Seed `changes/CH-001` (or next ID) with Frame assets aligned to MS-01 objective.
- Finalize planner seed + `planner_config.json` template to unlock deterministic Spec stage.
- Implement audit logging for stage transitions (linking to FR-29 acceptance criteria).
- Dry-run a full SpekKit cycle end-to-end; capture findings in `artifacts/phase1/demo/Week-01/` and adjust flow before human sign-off.
