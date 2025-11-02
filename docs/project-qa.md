# 🤖 Codexa.ai — Autonomous Agent Framework for Code Development and QA

---

## 1. Purpose

Design and implement an **autonomous, multi-agent framework** that manages the entire lifecycle of software code development — from design and implementation to testing, quality assurance, and controlled integration — under **human-in-the-loop governance**.

This framework, known as **Codexa.ai**, focuses exclusively on the **coding system itself**. It is the meta-layer that creates, tests, and improves software modules, not the downstream trading or runtime systems.

The system should:

* Operate autonomously day-to-day across design, code, and test tasks.
* Surface issues, clarifications, or exceptions to a human via **Discord chat**.
* Continuously improve through QA feedback and performance monitoring.
* Maintain complete transparency, auditability, and reproducibility.

---

## 2. Vision

* Human oversight without bottlenecks — the human is a **governor**, not a gatekeeper.
* Agents drive architecture, code, and test refinement loops.
* End-to-end quality control replaces manual PR review.
* Every action is logged, explainable, and auditable.
* Discord chat provides real-time visibility, commands (`/status`, `/clarify`, `/promote`), and alerts.

**Guiding Principles**

1. **Autonomy within Guardrails** — agents act freely inside defined quality and safety constraints.
2. **Evidence-Based Quality** — QA gates and reproducible test results replace subjective review.
3. **Human-in-the-Loop Governance** — human governs plans, policy shifts, and phase promotion.
4. **Transparency & Traceability** — every decision logged and auditable.
5. **Continuous Improvement** — agents learn from QA metrics and drift analysis.

---

## 3. Architecture Overview

### Core Roles

| Role                     | Description                                                                            |
| ------------------------ | -------------------------------------------------------------------------------------- |
| **Project Manager (PM)** | Orchestrates workflow, maintains plan + detail docs, runs QA, merges per policy.       |
| **Designer**             | Defines system architecture, module specs, and interfaces. Responds to clarifications. |
| **Implementer**          | Generates or refines code modules. Raises concerns upward.                             |
| **Tester**               | Maintains test plan + results. Executes QA gates.                                      |
| **Human Reviewer**       | Reviews plans, validates QA completion, approves promotions or high-impact changes.    |

### System Layers

1. **Audit & Handoff Bus** — persistent JSONL/SQLite log for all actions, concerns, and commands.
2. **Discord Bridge** — two-way chat interface for alerts and commands.
3. **GitOps Layer** — branch-based autonomy with QA-driven merges and tagging.
4. **QA Engine** — continuous end-to-end testing; produces `QA_REPORT.md`.
5. **Policy Engine** — defines thresholds for merge, promotion, and escalation.

### Agent Communication Flow

```
 ┌────────────────────────────┐
 │        Human Reviewer      │
 │  (Governance & Oversight)  │
 └────────────┬───────────────┘
              │  (review / commands)
 ┌────────────┴───────────────┐
 │     Project Manager (PM)   │
 │  - Coordinates workflow    │
 │  - Runs QA & merges        │
 │  - Escalates concerns      │
 └────────────┬───────────────┘
              │ handoffs / logs
 ┌────────────┼────────────┐
 │  Designer  │ Implementer│ Tester │
 │  (specs)   │ (code)     │ (tests)│
 └────────────┴────────────┴────────┘
              │
       Audit / Handoff Bus
              │
       Discord Bridge + GitOps Layer
```

---

## 4. Governance Model

* **Human reviews** only:

  * Project plans and phase roadmaps.
  * High-impact architectural or structural variations.
  * End-to-end QA promotion candidates.
* **Agents may**:

  * Merge, commit, and test freely inside sandbox branches.
  * Auto-merge to integration branch when QA gates pass.
* **Escalation:** Any agent can raise a concern → PM → Human. Concerns appear instantly in Discord (`#codexa-concerns`) and can be acknowledged or resolved interactively.

---

## 5. Communication Interface (Discord Bot)

Commands:

```
/status                 → show current phase, agents, open concerns
/clarify <agent> [msg]  → request explanation
/ack <id>               → acknowledge issue
/resolve <id>           → close concern
/promote <phase>        → approve phase merge + tag
/pause <agent>          → suspend workflow
/resume <agent>         → resume workflow
```

All commands are logged in `/audit/commands.jsonl`.

---

## 6. Quality Assurance & Automation

**QA Policy (example defaults)**

```yaml
auto_merge_if:
  all_tests_passed: true
  coverage_min: 80
  reproducibility_min: 95
  lint_errors: 0
  build_passed: true
require_human_if:
  impact: high
  gate_fail: true
  phase_promotion: true
```

**QA Engine Output:** `QA_REPORT.md` summarizing test coverage, reproducibility, linting, and build metrics.

If any gate fails → escalate to Human.

---

## 7. Git Workflow

* Agents commit within `phaseX/*` branches.
* PM merges to `develop/` when QA gates pass.
* Human approves promotions (e.g., `develop` → `main`) via `/promote`.
* Audit logs mirror Git actions in `audit/git_actions.jsonl`.
* Daily automated commit of `PROJECT_DETAIL.md`, QA reports, and audit entries.

### Protection Rules

* Protected branches: `main`, `develop`.
* Required: QA pass or human approval.
* Automatic rollback on failed merge or post-merge regression.

---

## 8. Functional Requirements

### Agent Behaviour

1. Agents must:

   * Accept structured inputs (Markdown, JSON artifacts).
   * Produce defined outputs (docs, code, or logs).
   * Record all actions in `/audit/`.
   * Support upward concern escalation.

2. PM must:

   * Maintain `PROJECT_OVERVIEW.md` and `PROJECT_DETAIL.md`.
   * Execute QA and merge policies.
   * Escalate critical or unresolved events to Human.

3. Human must:

   * Review and approve phase promotions and design variations.
   * Interact via Discord commands.

### Communication & Escalation

* All agents must support upward concern flow.
* PM consolidates concerns and forwards to Human if unresolved.
* Discord bot manages alerts and commands.

### QA & Gates

* Automated QA verifies:

  * All tests pass.
  * Coverage ≥ policy.
  * Reproducibility ≥ threshold.
  * Drift under threshold.
  * No unresolved critical concerns.

---

## 9. Non-Functional Requirements

| Category            | Requirement                                                  |
| ------------------- | ------------------------------------------------------------ |
| **Auditability**    | All actions logged with timestamp and hash.                  |
| **Transparency**    | Each file change linked to a handoff record.                 |
| **Reliability**     | No silent failures; alerts reach Human in <30s.              |
| **Security**        | Agents have scoped credentials; protected branches enforced. |
| **Scalability**     | Supports multiple parallel code projects.                    |
| **Reproducibility** | Every QA run can be reconstructed from artifacts and logs.   |

---

## 10. Implementation Plan

### Phase 0 — Framework Skeleton

* Establish repo structure, audit schema, Discord bridge mock.
* Define command structure and audit format.

### Phase 1 — QA Loop + Core Agents

* Implement PM, Designer, Implementer, Tester agents.
* Add QA engine and policy-based merge control.

### Phase 2 — CI/CD Integration

* Connect to build/test environments.
* Integrate automated linting, static analysis, and performance checks.

### Phase 3 — Full Autonomy + Self-Validation

* Enable continuous learning from QA outcomes.
* Introduce code quality scoring and self-adjusting policies.

---

## 11. Phase 0 – Immediate Deliverables

* [ ] Create repo skeleton (`docs/`, `audit/`, `pipelines/`, `tests/`, `gitops/`)
* [ ] Implement minimal `audit/logger.py` that writes JSONL + timestamps
* [ ] Add Discord webhook stub with dummy `/status` + `/clarify`
* [ ] Mock one agent (ProjectManager) calling `log_handoff()` + `log_concern()`
* [ ] Set up `QA_POLICY.yaml` parser (just validate config)
* [ ] Demo CLI: `make demo` → prints full audit + Discord log line

---

## 12. Agent Message Contract

```json
{
  "agent": "Implementer",
  "task": "generate_code",
  "inputs": ["design_spec.md"],
  "outputs": ["src/module_x.py"],
  "status": "completed",
  "timestamp": "2025-10-29T12:00:00Z"
}
```

This ensures consistent communication and logging between agents.

---

## 13. Minimal CLI Interface

```
make run          # starts agents + Discord stub
make qa           # runs QA gatekeeper
make audit        # prints audit summary
make clean        # clears temp logs
```

A few `Makefile` targets or shell scripts ensure reproducible workflows.

---

## 14. Versioning & Tagging Convention

```
v0.1.0-phase0
v0.2.0-phase1-qa
v0.3.0-phase2-ci
```

This provides a clear lineage of framework maturity and helps agents auto-tag.

---

## 15. Safety & Kill-Switch Policy

Any agent may trigger a global `/pause` command if audit integrity, reproducibility, or data corruption issues are detected.

All such events must be logged in `/audit/concerns.jsonl` and immediately surfaced to the Human via Discord.

---

## 16. Metrics & Observability

* **Dashboards:** Track agent activity, open concerns, QA metrics, and phase progress.
* **Metrics:**

  * Test coverage %, reproducibility %, build pass rate.
  * Concern response latency.
  * Mean QA cycle time.
  * Merge success/failure ratio.
* **Alerts:**

  * WARN — near-threshold metrics.
  * ALERT — QA fail or regression.
  * CRITICAL — data corruption, halted agent, or policy breach.
* **Reports:** Daily Discord summary and Markdown QA digest.

---

## 17. Acceptance Criteria

* Agents autonomously execute full code dev/test cycles.
* `/status` returns real-time project health.
* QA and audit logs reproducible and verifiable.
* Human intervenes only for governance actions.
* Git, audit, and Discord histories fully aligned.
