# CR001.3 Requirement Impact & Clarifications

## Context
- Change request `docs/CHANGE_REQUEST_001.3.md` builds on CR001.2 by introducing a maturity-adaptive delivery framework (levels M0–M4) that scales governance, traceability, and agent participation as the project evolves.
- New artifacts (`PROJECT_METADATA.md` / `project.yaml`, `PROCESS_MATURITY_GUIDE.md`) are required so agents can read the current maturity level, adjust enforcement logic, and record maturity upgrades.

## Updated Requirements
| Requirement ID | Current Focus | Required Update from CR001.3 | Effort (est.) | CR001.3 Source |
| --- | --- | --- | --- | --- |
| FR-01 | PM orchestrates workflows and approvals. | Detect `maturity_level`, activate only the roles appropriate for that level, and coordinate maturity upgrade proposals with Governance Officer. | Medium | Adaptive Rules for Agents → Project Manager; Workflow Summary. |
| FR-02 | PM-maintained status docs. | Surface current maturity level, planned upgrade criteria, and link to latest maturity review outcomes (`PROCESS_MATURITY_GUIDE.md`, `CHANGELOG.md`). | Low-Medium | Process Weight tables; Overview section. |
| FR-05 | Tester owns QA artifacts. | Align test depth expectations with maturity (e.g., sunny-day tests at M1, risk-based at M2, full suite at M3+); document the active maturity band inside QA deliverables. | Medium | Process Weight by Maturity → Testing row; Agent Behavior table. |
| FR-06 | Structured handoff/audit logging. | Log maturity level on each audit entry and record maturity upgrade events (category `Maturity Upgrade`) including verifier and criteria snapshots. | Low | Lifecycle Transitions; Implementation → ChangeLog requirement. |
| FR-10 | Human approval / governance gates. | Enforce maturity-specific approval gates (e.g., GO sign-off required from M2 upward) and document which maturity criteria were satisfied before HR approval. | Medium | Adaptive Rules → GO; Governance Weight by Level. |
| FR-11 | QA policy enforcement. | Make QA thresholds dynamic based on maturity (skip full enforcement at M0/M1, require at M2+, expand to ROI/risk gates at M3+). | Medium | Process Weight by Maturity → Change Evaluation & QA rows. |
| FR-13 | Status snapshots / metrics. | Include maturity level, time-in-level, and upcoming upgrade checklist status in every snapshot/dashboard. | Low-Medium | Workflow Summary; Lifecycle Transitions. |

## New Requirements
| Proposed ID | Requirement Summary | Primary Owner | Effort (est.) | Motivation from CR001.3 |
| --- | --- | --- | --- | --- |
| FR-32 (proposed) | Maintain `PROJECT_METADATA.md` (or `project.yaml`) capturing maturity level, last review date, readiness criteria, and next target level for agent consumption. | Project Manager / Governance Officer | Medium | Practical Implementation → Add project metadata file. |
| FR-33 (proposed) | Publish and maintain `docs/PROCESS_MATURITY_GUIDE.md` describing expectations, agent participation, and deliverables for M0–M4. | Governance Officer | Low-Medium | Provided guide at end of CR001.3. |
| FR-34 (proposed) | Implement maturity gate reviews run by Governance Officer, producing upgrade recommendations and logging decisions as `CH-###` entries. | Governance Officer | Medium | Practical Implementation → Maturity Gate Reviews; Lifecycle Transitions. |
| FR-35 (proposed) | Enable agents (PM, GO, CE, IM, QA/TQA) to adapt prompts/behavior automatically based on `maturity_level` (e.g., skip enforcement at M0, full suite at M4). | Platform / Agent Owners | High | Adaptive Rules for Agents; Agent Behavior table. |
| FR-36 (proposed) | Track maturity metrics (time in level, number of upgrades, active criteria) and expose via `/status change` or dashboards. | Project Manager / Analytics owner | Medium | Workflow Summary; Recommendation bullets. |

## Effort Notes
- **High**: Cross-agent prompt/logic updates (FR-35) will require coordinated scripting and regression tests.
- **Medium**: New artifacts, maturity gating logic, and dynamic reporting.
- **Low**: Documentation updates or metadata fields layered onto existing structures.

## Suggested Refinements
- Start with a lightweight `PROJECT_METADATA.md` keyed by maturity level before wiring agents for full automation; treat metadata as the single source of truth.
- Pilot maturity-aware enforcement in QA/GO agents first (highest leverage) before extending to all roles.
- Consider deriving some maturity metrics from existing audit logs to avoid duplicating instrumentation.

## Clarification Questions
1. How frequently should maturity reviews occur (per sprint, per milestone, or ad hoc when criteria met)?
Per milestone delivered, or if human requests a review and/or a change.
2. Do you prefer a single metadata file per repo or per project/phase when multiple efforts run in parallel?
Give me a proposal on this, the pros and cons of each approach, and a recommended path forward.
3. What minimum evidence is required for a maturity upgrade (e.g., specific coverage %, stakeholder sign-off)?
We will define this during implementation based on the maturity level being targeted.
4. Should agent behavior fall back automatically when maturity is downgraded, or are downgrades out of scope?
Downgrades are in scope, yes fall back automatically if a downgrade occurs, but we will not reprocess previous items.
5. Where would you like maturity metrics surfaced first (`PROJECT_OVERVIEW.md`, CLI `/status`, dashboards), and who consumes them most?
Both .. we need a permanent record in PROJECT_OVERVIEW.md and also surfaced in the CLI for quick checks.
