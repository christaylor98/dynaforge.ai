# Code Overlord Requirements

## 1. Functional Requirements

| ID | Requirement | Notes / Rationale |
| -- | ----------- | ----------------- |
| FR-01 | Provide a Project Manager agent that captures objectives in `REQUIREMENTS.md`, maintains project summaries, and coordinates workflows across agents. | Enables controlled initiation and traceability of deliverables. |
| FR-02 | Maintain two PM-authored status documents: `docs/PROJECT_OVERVIEW.md` (executive snapshot) and `docs/PROJECT_DETAIL.md` (task-level plan with commentary). | Supports the dual-visibility governance model described in brainstorming notes. |
| FR-03 | Allow Designer agent to produce and update `design/ARCHITECTURE.md` and `design/DESIGN_SPEC.md`, including responses to `/clarify Designer …` requests. | Ensures architecture decisions are explicit and reviewable. |
| FR-04 | Ensure Implementer agents generate code artifacts per approved design, attach handoff metadata, and respect policy-defined branch naming (`phaseX/<agent>`). | Keeps execution aligned with design intent and audit expectations. |
| FR-05 | Provide Tester agent ownership of `tests/TEST_PLAN.md`, `tests/TEST_RESULTS.md`, and `tests/TEST_RESULTS_DETAIL.md`, capturing coverage, reproducibility, and drift metrics. | Delivers evidence-driven quality gates. |
| FR-06 | Log every inter-agent handoff as structured JSON (`/audit/handoff_*.json`) containing origin, destination, summary, impact level, and referenced artifacts. | Required for auditability and governance. |
| FR-07 | Record concerns via a standardized API (`log_concern`) that writes to `/audit/concerns.jsonl`, mirrors entries into `PROJECT_DETAIL.md`, and notifies Discord (`#agent-concerns`). | Supports rapid escalation and human awareness. |
| FR-08 | Implement a Discord bridge that supports outbound alerts and inbound commands (`/status`, `/clarify`, `/ack`, `/resolve`, `/assign`, `/pause`, `/resume`, `/promote`). | Enables human-in-the-loop governance without leaving chat. |
| FR-09 | Track Discord commands in `/audit/commands.jsonl` and ensure targeted agents respond or adjust workflow accordingly. | Maintains full command audit trail and accountability. |
| FR-10 | Enforce human approval for project plan changes, high-impact variations, and phase promotions; approvals must be captured inline in Markdown artifacts. | Provides governance gates that align with the defined oversight model. |
| FR-11 | Integrate a policy/QA engine that evaluates QA results against thresholds (coverage, reproducibility, drift) before permitting merges to `develop`. | Replaces manual PR review with evidence-based gating. |
| FR-12 | Support GitOps workflows with protected `main` and `develop` branches, structured commit metadata, and automated tagging (`v0.x-phaseY`) upon promotion. | Ensures consistent release management and traceability. |
| FR-13 | Produce regular status snapshots (`status.json`, dashboards, or Markdown digests) summarizing phase progress, open concerns, and key metrics. | Keeps human supervisor informed between active interactions. |
| FR-14 | Provide rollback or pause mechanisms (`/pause`, `/resume`, automatic revert scripts) when QA gates fail or critical concerns arise. | Delivers safety controls for autonomous operations. |

## 2. Non-Functional Requirements

| Category | Requirement |
| -------- | ----------- |
| Auditability | All actions (handoffs, concerns, commands, merges, approvals) must be timestamped, linked to artifacts, and reproducible from version control. |
| Transparency | Each artifact change references its originating handoff; humans can trace any decision through Markdown and audit logs. |
| Reliability | Critical alerts must reach the human within 30 seconds; command acknowledgments must be persisted without loss. |
| Security | Agents use scoped credentials; protected branches prevent unapproved merges; kill-switch commands are always honored. |
| Scalability | Framework supports multiple simultaneous projects by namespacing branches, audit logs, and Discord threads. |
| Reproducibility | QA runs are deterministic with ≥95% reproducibility; artifacts capture seeds, configurations, and data references. |
| Observability | System exposes metrics (coverage %, drift %, open concerns, SLA compliance) and daily summaries for trend analysis. |
| Maintainability | Components (agents, policy engine, Discord bridge) are modular with clear interfaces and configuration files (`agents.yaml`, `QA_POLICY.yaml`). |

## 3. Constraints & Assumptions
- Human reviewer has final authority over plan approvals, high-impact variations, and phase promotions.
- Agents operate in a controlled Git environment with network access restricted to approved services (Discord, repository host).
- Markdown artifacts and audit logs are the source of truth for status reporting; no hidden state.
- Policy thresholds (coverage %, drift %, etc.) are configurable but must default to conservative baselines (e.g., coverage ≥80%).

## 4. Acceptance Criteria
- End-to-end agent loop (PM → Designer → Implementer → Tester → Human) executes on a reference task with all handoffs logged and approvals recorded.
- Discord `/status` returns phase, task counts, and concern statistics derived from live audit data.
- QA engine blocks promotions when policy thresholds are missed and raises a concern automatically.
- Human-triggered `/promote` results in tagged release and archival of phase artifacts with matching audit entries.
- All concerns logged during a cycle can be traced from Discord messages back to `concerns.jsonl` and resolved with documented responses.

## 5. Phase Roadmap Alignment
- **Phase 0** must deliver repository scaffolding, baseline logging utilities, and a Discord stub with `/status` + `/clarify`.
- **Phase 1** must implement core agents, QA policy enforcement, concern logging, and human approval hooks.
- **Phase 2** must add CI/CD integration, linting/static analysis hooks, and expanded observability (dashboards, drift detection).
- **Phase 3** must enable adaptive policy tuning and extended agent roles, leveraging accumulated QA and concern data.

