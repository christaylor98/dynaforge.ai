# Code Overlord Architecture

## System Overview
Code Overlord is a multi-agent orchestration layer that manages the full software lifecycle under human governance. The system is organized into coordinated layers:

```
┌───────────────────────────────────────────────────────────┐
│                    Human Governance Layer                  │
│ (approvals, commands, status requests via chat/CLI/web)    │
└───────────────▲───────────────────────────────┬────────────┘
                │     inbound commands          │ outbound status
┌───────────────┴──────────────┐     ┌──────────┴───────────┐
│  Project Management Layer     │     │  Concern & Command    │
│  (PM agent, policy engine)    │     │  Bridge (interface)   │
└───────────────▲──────────────┘     └──────────▲───────────┘
                │                               │
┌───────────────┴──────────────┐     ┌──────────┴───────────┐
│    Execution Agents           │     │     Observability     │
│ (Designer, Implementer, Tester│     │   (status snapshots,  │
│    + optional specialists)    │     │      dashboards)      │
└───────────────▲──────────────┘     └──────────▲───────────┘
                │                               │
┌───────────────┴────────────────────────────────┴───────────┐
│                 Audit & Artifact Persistence                │
│  (Markdown docs, JSONL handoffs, git branches, reports)     │
└────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agents
- **Project Manager (PM)**: Orchestrates work, maintains requirements and plan documents, enforces policy gates, and coordinates human reviews.
- **Designer**: Produces architecture and module specifications, handles `/clarify Designer ...` requests, and updates design artifacts.
- **Implementer(s)**: Generate source code per approved designs and emit handoff metadata for every change.
- **Tester**: Owns QA plans, executes tests, writes results, and raises concerns when coverage or reproducibility fall below thresholds.
- **Optional Specialists**: Future roles (Optimizer, Observer, etc.) integrate via the same handoff and audit patterns.

### 2. Audit & Handoff Bus
- JSONL or SQLite-backed store under `/audit/` for handoffs (`handoff_*.json`), concerns (`concerns.jsonl`), and commands (`commands.jsonl`).
- Every handoff records origin, destination, purpose, artifact paths, summary, impact level, and status.
- Ties directly into Git metadata (commit IDs, branch names) and Markdown change logs.

### 3. Documentation & Artifact Layer
- Persistent Markdown documents tracked in Git: `REQUIREMENTS.md`, `docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_DETAIL.md`, design specs, and test reports.
- Test outputs (`QA_REPORT.md`, `tests/TEST_RESULTS_DETAIL.md`) and generated metrics stored under `artifacts/` when large.
- Human approvals appended inline (e.g., `✅ Approved by Human 2025-10-29`) to maintain full audit history.

### 4. Policy & QA Engine
- Reads `QA_POLICY.yaml` / `.project_policies.yaml` to determine merge and promotion thresholds (coverage %, drift %, gating rules).
- Controls automatic merges to integration branches when criteria are met.
- Produces summary evaluations for the human reviewer before promotions.

### 5. Discord Bridge
- Provides outbound notifications (concerns, status updates) and inbound command parsing.
- Commands (`/status`, `/clarify`, `/ack`, `/resolve`, `/promote`, `/pause`, `/resume`) write structured entries to the audit store for agent consumption.
- Ensures human responses are mirrored back to Markdown and audit artifacts.
- Abstracts the interface layer so additional adapters (CLI tool, web console) can reuse the same command schema without changing downstream agents.

### 6. GitOps Layer
- Branch hierarchy: `main` (human-controlled), `develop` (integration), and `phaseX/<agent>` working branches.
- Agents commit with structured metadata (`Signed-off-by`, `Audit-ID` footers) and open PRs through Git APIs.
- PM agent merges only after policy checks and human approvals; tags releases per phase (`v0.2.0-phase1-qa`).

### 7. Observability & Status Services
- Periodically publishes `status.json` snapshots for `/status` command responses.
- Generates daily dashboards or Markdown digests summarizing open concerns, QA metrics, and phase progress.
- Tracks SLA compliance (e.g., alert acknowledgment times).

### 8. Human Interaction Flow
1. Human invokes a command (currently Discord; future CLI/web adapters plug in through the same API surface).
2. Interface adapter normalizes the request into a `Command Object` and appends it to `/audit/commands.jsonl`.
3. Command router notifies the Project Manager or targeted agent; they act and produce a response artifact or status update.
4. Response is written back to the audit store and surfaced through the interface adapter (chat reply, CLI printout, or web notification).
5. Any resulting changes (plan updates, approvals, pauses) propagate through documentation, Git, and observability layers, ensuring closed-loop governance.

## Process Flow
1. **Initiation**: PM ingests a goal, updates `REQUIREMENTS.md`, and issues tasks to Designer and other agents (tracked in `docs/PROJECT_DETAIL.md`).
2. **Design**: Designer drafts `design/ARCHITECTURE.md` and `design/DESIGN_SPEC.md`; human must approve high-impact changes.
3. **Implementation**: Implementer branches from `phaseX/` namespace, commits code, and logs handoff records that reference updated files.
4. **Testing**: Tester executes planned suites, records results, and updates QA metrics. Failures trigger `log_concern()` entries and Discord alerts.
5. **Governance Review**: Human reviews project plan, high-impact variations, and test results through the interaction adapter (Discord today, CLI/web later); approvals recorded in docs.
6. **Promotion**: PM agent validates policy gates, merges into `develop`, and requests human `/promote` for tagging releases.
7. **Feedback Loop**: Concerns and QA metrics feed into policy adjustments and roadmap updates captured in Markdown and audit logs.

## Data Contracts
- **Handoff Record**: `{ from, to, purpose, inputs[], outputs[], impact, summary, status, timestamp }`
- **Concern Object**: `{ id, from, to, severity, category, summary, details, timestamp, status }`
- **Command Object**: `{ cmd, target, args, user, timestamp, linkage }`

These contracts guarantee deterministic processing across agents and support reproducible audits.

## Phase-specific Architecture Considerations
- **Phase 0**: Minimal viable components—file hierarchy, logging utilities, Discord stub, PM agent prototype.
- **Phase 1**: Full agent loop, QA policy enforcement, concern escalation, and human approvals wired end-to-end.
- **Phase 2**: Integrate CI/CD runners, static analysis, performance benchmarking, and richer observability dashboards.
- **Phase 3**: Adaptive policy engine, automated drift detection, and expanded agent roster with self-validation workflows.

## Security & Safety
- Scoped credentials per agent; protected branches enforce human approvals.
- `/pause` and `/resume` commands act as kill-switch controls.
- Automated rollback scripts revert merges when post-merge QA fails.
- All sensitive operations (high-impact variations, policy edits) require explicit human confirmation and are timestamped.
