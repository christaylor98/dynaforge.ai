# CR001.2 Requirement Impact & Clarifications

## Context
- Change request `docs/CHANGE_REQUEST_001.2.md` extends CR001.1 with a formal change-management lifecycle: structured change objects (`CH-###`), automated change routing, value/risk evaluation gates, and expanded metrics.
- New agents (Change Evaluator, Vision Validator) and processes (Change Router, change metrics dashboard) are introduced, requiring updates to existing governance, auditing, and documentation workflows.

## Updated Requirements
| Requirement ID | Current Focus | Required Update from CR001.2 | Effort (est.) | CR001.2 Source |
| --- | --- | --- | --- | --- |
| FR-01 | PM coordination and approvals. | Integrate Change Evaluator/Governance gates before approvals, maintain change metrics, and orchestrate partial approvals. | Medium | Change Evaluation Loop → PM interactions; Recommendation → Phase 1–4 sequencing. |
| FR-02 | PM-authored status docs. | Embed change summaries, evaluation outcomes, and change velocity metrics (`CHANGELOG.md`, ROI dashboards). | Medium | Practical Implementation Steps → Add `CHANGELOG.md`; Option D metrics. |
| FR-06 | Structured audit logs. | Extend schema with `change_id`, partial approval status, ROI fields, and cross-links to change artifacts. | Low-Medium | Change Flow Infrastructure → audit schema extension. |
| FR-10 | Human approval checkpoints. | Enforce three-gate approval (Impact, Evaluation, Governance) before HR sign-off; support partial approvals. | Medium | Change Evaluation Loop → approval flow; Workflow diagram. |
| FR-11 | QA gate before merges. | Consume Change Evaluator and Governance outputs to block merges when evaluation or governance gates fail. | Medium | Benefits table; workflow (CE→GO→PM) prior to execution. |
| FR-13 | Status snapshots / metrics. | Include change density, change-to-delivery lag, vision drift index, and stability ratio in regular snapshots. | Medium | Option D → Change Velocity Metrics; Recommendation sequencing. |

## New Requirements
| Proposed ID | Requirement Summary | Primary Owner | Effort (est.) | Motivation from CR001.2 |
| --- | --- | --- | --- | --- |
| FR-25 (proposed) | Implement Change Objects (`CH-###`) with `CHANGELOG.md` capturing summary, affected FR/WS/TC, decision history, and approvers. | Project Manager / Governance Officer | Medium | Option A — Change Flow Infrastructure; Practical Implementation Step 1. |
| FR-26 (proposed) | Extend audit schema and CLI (`/impact`, `/change`, `/approve`) to register, review, and close change objects. | Governance Officer / Interaction Stub owner | Medium | Option A → command hooks; Implementation Steps 2 & 3. |
| FR-27 (proposed) | Deploy Change Router watcher to trigger RA→IA→... loop on requirement/document diffs. | Implementation Manager | High | Option B — Embed Change Handling; Implementation Step 3. |
| FR-28 (proposed) | Introduce Change Evaluator agent producing ROI/risk recommendations (`CHANGE_EVALUATION.md`) with approve/defer outcomes. | Change Evaluator | High | Change Evaluation Loop; Change Evaluator section. |
| FR-29 (proposed) | Stand up Vision Validator agent to score alignment with `VISION.md` / `ARCHITECTURE.md` and feed CE recommendations. | Vision Validator | Medium | Option C — Vision Anchoring; Workflow diagram (PM↔VV↔CE). |
| FR-30 (proposed) | Implement change velocity dashboard (metrics: density, lag, vision drift, stability ratio) and expose via `/status change`. | Project Manager / Analytics owner | Medium | Option D — Metrics & Optimization; Recommendation table. |
| FR-31 (proposed) | Add partial approval handling (e.g., CH-012a/b), enabling IM to decompose approved portions while deferring remainder. | Implementation Manager | Medium | Change Evaluation Loop → Partial Approve guidance. |

## Effort Notes
- **High**: Requires new agents/services and orchestration changes (Change Router, Change Evaluator).
- **Medium**: Significant schema, workflow, or documentation updates (status dashboards, change metrics).
- **Low**: Minor schema or configuration extension (additional audit fields).

## Suggested Refinements
- Consider piloting the Change Evaluator as an extension of the Project Manager agent before dedicating a new role, reducing upfront prompt proliferation.
- Leverage existing CI hooks for the Change Router instead of introducing a new daemon; a Git-based watcher may cover most cases with lower ops overhead.
- For metrics, start with weekly snapshots aggregated from audit logs before building a live dashboard to avoid premature complexity.

## Clarification Questions
1. How do you prioritize **value vs. disruption** when the Change Evaluator scores a proposal (e.g., is ROI ≥ 1.5 the threshold for “Approve”)?
Will define during implementation - up to the human to make the final call, AI should provide a recommendation based on defined criteria.
2. Should partial approvals result in distinct `CH-###` entries, or can we track sub-decisions within one change record (e.g., sections within `CHANGE_EVALUATION.md`)?
One change record with sub-decisions tracked within it.
3. Do you want the Vision Validator to block changes automatically, or act as an advisory signal within the Change Evaluator report?
Advisory signal within the Change Evaluator report.
4. For change velocity metrics, which cadence matters most to you (per commit, daily, weekly), and where should those metrics surface (`PROJECT_OVERVIEW.md`, CLI, dashboards)?
Weekly cadence and/or per milestone; surface in dashboards and CLI.
5. Are the new CLI commands expected to function offline (local-only) or interact with remote services/Discord integrations?
Both if possible, want to make it as flexible as possible.

Let me know your preferences so we can refine the requirement updates and proceed with amending `docs/REQUIREMENTS.md` and related artifacts.
