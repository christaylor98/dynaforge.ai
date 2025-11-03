# Codexa.ai Architecture

## System Overview
Codexa.ai is a multi-agent orchestration layer that manages the full software lifecycle under human governance. The system is organized into coordinated layers:

```
┌───────────────────────────────────────────────────────────┐
│                    Human Governance Layer                  │
│ (approvals, commands, status requests via CLI/messaging)   │
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
│            Discovery & Understanding Layer                  │
│  (Discovery CLI, System Model Graph YAML, change seeds)     │
└───────────────▲────────────────────────────────┬───────────┘
                │                                │
┌───────────────┴────────────────────────────────┴───────────┐
│                 Audit & Artifact Persistence                │
│  (Markdown docs, JSONL handoffs, git branches, reports)     │
└────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agents
- **Project Manager (PM)**: Orchestrates work, maintains requirements and plan documents, enforces policy gates, and coordinates human reviews. In MS-02 the PM also conducts the loop-planning conversation (“What should we execute next?”) that bridges discovery outputs into execution.
- **Designer**: Produces architecture and module specifications, responds to clarification prompts, and updates design artifacts.
- **Implementer(s)**: Generate source code per approved designs and emit handoff metadata for every change.
- **Tester**: Owns QA plans, executes tests, writes results, and raises concerns when coverage or reproducibility fall below thresholds.
- **Discovery Analyzer**: Executes `codexa discover` flows, produces structural/behavioural/intent manifests, and refreshes the System Model Graph projections with iteration metadata.
- **Seed Planner**: Consumes the PM’s loop plan (requirement/change/phase/milestone scope) and materialises the seed bundle (`codexa seed --from loop-plan`) with context slices, manifests, and baseline tests.
- **Analytics Lead**: Maintains understanding coverage and change readiness metrics surfaced through `/status` and conversational prompts.
- **Interaction Bridge**: Normalises natural-language human prompts (approvals, follow-ups, loop planning) into agent directives while keeping CLI aliases available for deterministic playback.
- **Optional Specialists**: Future roles (Optimizer, Observer, etc.) integrate via the same handoff and audit patterns.

### 2. Audit & Handoff Bus
- JSONL or SQLite-backed store under `/audit/` for handoffs (`handoff_*.json`), concerns (`concerns.jsonl`), and commands (`commands.jsonl`).
- Every handoff records origin, destination, purpose, artifact paths, summary, impact level, and status.
- Ties directly into Git metadata (commit IDs, branch names) and Markdown change logs.

### 3. Documentation & Artifact Layer
- Persistent Markdown documents tracked in Git: `REQUIREMENTS.md`, `docs/PROJECT_OVERVIEW.md`, `docs/PROJECT_DETAIL.md`, design specs, and test reports.
- Test outputs (`QA_REPORT.md`, `tests/TEST_RESULTS_DETAIL.md`) and generated metrics stored under `artifacts/` when large.
- Human approvals appended inline (e.g., `✅ Approved by Human 2025-10-29`) to maintain full audit history.
- Discovery artifacts (`analysis/system_manifest.yaml`, `analysis/change_zones.md`, `analysis/intent_map.md`) and System Model Graph YAML projections remain the canonical understanding snapshot.
- MS-02 introduces iterative artifacts: `docs/status/iteration_log.md` (discovery follow-up history), `changes/CH-###/seed/REVIEW.md` (living review digest synthesised from human feedback), and governance roll-ups (`artifacts/ms02/storyboard/summary.md`, `gaps.md`) that record every decision point.

### 4. Policy & QA Engine
- Reads `QA_POLICY.yaml` / `.project_policies.yaml` to determine merge and promotion thresholds (coverage %, drift %, gating rules).
- Controls automatic merges to integration branches when criteria are met.
- Produces summary evaluations for the human reviewer before promotions.

### 5. Interaction Bridge
- Conversational prompts are the default interface (“approve design for CH-010”, “assign gaps to IA”). The bridge interprets intent, maps it onto internal command objects, and captures the conversation transcript in audit logs.
- Deterministic CLI aliases remain for playback and scripting (`codexa discover`, `codexa loop plan`, `codexa approve scope`), but they are optional.
- Messaging and CLI adapters share the same command schema, ensuring human responses propagate into Markdown and audit artifacts regardless of entry point.
- Optional adapters (web console, chat integrations) can reuse the same prompt grammar without changing downstream agents.

### 6. GitOps Layer
- Branch hierarchy: `main` (human-controlled), `develop` (integration), and `phaseX/<agent>` working branches.
- Agents commit with structured metadata (`Signed-off-by`, `Audit-ID` footers) and open PRs through Git APIs.
- PM agent merges only after policy checks and human approvals; tags releases per phase (`v0.2.0-phase1-qa`).

### 7. Observability & Status Services
- Periodically publishes `status.json` snapshots for `/status` command responses.
- Generates daily dashboards or Markdown digests summarizing open concerns, QA metrics, and phase progress.
- Tracks SLA compliance (e.g., alert acknowledgment times).
- Surfaces understanding coverage %, discovery freshness timestamps, and change readiness heatmaps sourced from the System Model Graph.

### 8. Human Interaction Flow
1. Human invokes a command through the Python CLI or messaging client; future adapters can reuse the same API surface.
2. Interface adapter normalizes the request into a `Command Object` and appends it to `/audit/commands.jsonl`.
3. Command router notifies the Project Manager or targeted agent; they act and produce a response artifact or status update.
4. Response is written back to the audit store and surfaced through the interface adapter (CLI stdout, messaging acknowledgment, or other registered adapters).
5. Any resulting changes (plan updates, approvals, pauses) propagate through documentation, Git, and observability layers, ensuring closed-loop governance.

### 9. Discovery & Understanding Layer
- **Context Intake:** Humans can attach folders, wiki exports, or unstructured notes. The ingestion helper indexes parsable material, logs `context_unparsed` items, and feeds references into discovery.
- **Discovery Execution:** `codexa discover --config docs/discovery/config.yaml` runs full-mode analysis by default, streaming progress telemetry and refreshing manifests plus the System Model Graph. Quick mode remains available when humans request it.
- **Iteration Loop:** Each discovery run appends to `docs/status/iteration_log.md`, raises follow-up IDs, and accepts conversational approvals/dismissals to avoid unnecessary reruns.
- **Loop Planning & Seeds:** `codexa loop plan` captures the chosen execution scope (requirement/change/phase/milestone). `codexa seed --from loop-plan` packages scoped context, manifests, and baseline tests with traceability hooks back to discovery artifacts.
- **Understanding Metrics:** Coverage and readiness scores calculated from manifests/System Model Graph updates feed directly into `/status`, governance summaries, and milestone storyboard artifacts.

## Process Flow (MS-02 + MS-01)
1. **Context Intake (optional)** — Humans attach roots, docs, or scratch notes; the system indexes what it can and reports anything unreadable.
2. **Discovery Run** — `codexa discover --config docs/discovery/config.yaml` executes, streaming progress and refreshing manifests/System Model Graph projections.
3. **Iteration Review** — The AI posts an iteration summary with follow-up IDs in `docs/status/iteration_log.md`, accepts conversational “accept/dismiss” prompts, and only re-runs discovery when required.
4. **Requirement Curation** — Raw human material is ingested, normalised into curated FRs, and linked to discovery artifacts; changes (`CH-###`) are raised once context is clear.
5. **Loop Planning** — PM prompts the human for execution scope (requirement/change/phase/milestone). The decision is stored in `loop-plan.json`.
6. **Seed Generation** — Seed Planner runs `codexa seed --from loop-plan`, creating scoped bundles (`changes/CH-###/seed/`).
7. **Review & Approvals** — Humans provide free-form feedback; the AI reconciles it into `changes/CH-###/seed/REVIEW.md` and blocks progress until required approvals or waivers are recorded.
8. **Governance Summary** — Orchestrator compiles `summary.md`/`gaps.md`, prompts for publication approval, and handles any remaining remediation tasks.
9. **Execution Rail (MS-01)** — `codexa loop start --from loop-plan` feeds the prepared scope into the established PM → Designer → Implementer → Tester loop with existing QA/governance gates.
10. **Feedback & Metrics** — Outcomes, metrics, and new discovery insights roll back into the iteration log, requirements, and governance documentation.

## Data Contracts
- **Handoff Record**: `{ from, to, purpose, inputs[], outputs[], impact, summary, status, timestamp }`
- **Concern Object**: `{ id, from, to, severity, category, summary, details, timestamp, status }`
- **Command Object**: `{ cmd, target, args, user, timestamp, linkage }`

These contracts guarantee deterministic processing across agents and support reproducible audits.

## Phase-specific Architecture Considerations
- **Phase 0**: Minimal viable components—file hierarchy, logging utilities, CLI prototype with messaging stub, PM agent prototype.
- **Phase 1**: Full agent loop, QA policy enforcement, concern escalation, and human approvals wired end-to-end.
- **Phase 2**: Integrate CI/CD runners, static analysis, performance benchmarking, and richer observability dashboards.
- **Phase 3**: Adaptive policy engine, automated drift detection, and expanded agent roster with self-validation workflows.

## Security & Safety
- Scoped credentials per agent; protected branches enforce human approvals.
- `/pause` and `/resume` commands act as kill-switch controls.
- Automated rollback scripts revert merges when post-merge QA fails.
- All sensitive operations (high-impact variations, policy edits) require explicit human confirmation and are timestamped.
