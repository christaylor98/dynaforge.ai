# 🧩 Codexa_WORKFLOW.md — Autonomous Coding Workflow

## 1. Purpose

Define the operating workflow for **Codexa.ai**, focusing on maintaining a high degree of autonomy while ensuring architectural, requirements, and testing documentation remain synchronized and accurate.

This workflow minimizes human intervention — the system must self-report, self-correct, and surface concerns rather than require manual oversight.

---

## 2. Workflow Principles

1. **Autonomy First** – Agents should drive progress end-to-end, only escalating when policies or confidence thresholds are violated.
2. **Transparency Over Intervention** – Human visibility through dashboards and Discord is preferred to direct commands.
3. **Source of Truth Documents** – `ARCHITECTURE.md`, `REQUIREMENTS.md`, and `TEST_PLAN.md` are always current and regenerated as part of QA.
4. **Progress as a Deliverable** – `PROGRESS.md` acts as the live narrative of system evolution, updated automatically.
5. **Audit and Evidence-Based Validation** – Every step leaves verifiable artifacts in `/audit/`.

---

## 3. Core Workflow Loop (MS-02+)

### 3.1 Discovery → Execution Rail

```
[Context Intake] → [Discovery Analyzer] → [Iteration Loop]
        ↓                 ↓                    ↓
   [Requirements Curation] → [Loop Planning Prompt]
                     ↓
          [Seed Planner] → [Review & Approvals]
                     ↓
          [Governance Summary] → [PM→Designer→Implementer→Tester]
```

1. **Context Intake** (optional) captures human-provided folders, wiki exports, or notes; unparsed items become follow-ups.
2. **Discovery Analyzer** runs `codexa discover --config docs/discovery/config.yaml`, streaming telemetry and refreshing manifests/System Model Graph projections.
3. **Iteration Loop** records follow-ups in `docs/status/iteration_log.md`; humans resolve them with conversational prompts (“accept follow-up issue-12”).
4. **Requirements Curation** normalises raw human input into curated FRs linked to discovery artifacts before raising/updating `CH-###` records.
5. **Loop Planning Prompt** (“What should we execute next?”) captures scope (requirement/change/phase/milestone) and writes it to `loop-plan.json`.
6. **Seed Planner** materialises `codexa seed --from loop-plan`, producing scoped bundles with manifests, context, and baseline tests.
7. **Review & Approvals** occur via prompt-first conversation; the system synthesises feedback into `changes/CH-###/seed/REVIEW.md` and blocks progression until design/test approvals (or waivers) are logged.
8. **Governance Summary** compiles `artifacts/ms02/storyboard/summary.md` + `gaps.md`, prompting the human before publishing or scheduling remediation.
9. **Execution Rail** uses the established MS-01 loop (PM → Designer → Implementer → Tester) once `codexa loop start --from loop-plan` is invoked.

---

### 3.2 Human-in-the-Loop Checkpoints

Humans interact primarily through **prompt-first exchanges** handled by the Interaction Bridge. Typical prompts:

- “approve design for CH-010” — records design approval for the current loop plan.
- “assign gap-03 to impact assessor” — updates `gaps.md` and iteration log ownership.
- “publish governance report” — triggers summary publication once outstanding items are resolved or waivers recorded.

Deterministic CLI aliases (e.g., `codexa status`, `codexa loop plan`, `codexa approve scope --from loop-plan`) remain available for scripting or audits but are optional.

Skip protection ensures mandatory checkpoints (design/test approvals, resolved gaps) are acknowledged before progression; otherwise the orchestrator explains blockers and offers to log waivers or schedule follow-ups.

### 3.3 Dry Run Automation

Use `python3 scripts/ms02_dry_run.py` to populate sample artifacts (`docs/status/iteration_log.md`, `loop-plan.json`, `artifacts/ms02/storyboard/summary.md`, `gaps.md`) when rehearsing the storyboard or onboarding new contributors. Arguments can override scope, coverage, and follow-up IDs; run `python3 scripts/ms02_dry_run.py --help` for details.

---

## 4. Continuous Documentation Flow

* **`ARCHITECTURE.md`** – auto-updated when structure or API contracts change.
* **`REQUIREMENTS.md` / `docs/REQUIREMENTS_1_3.md`** – updated with coverage, completion %, traceability, and discovery evidence links.
* **`TEST_PLAN.md` / `TEST_RESULTS.md`** – live reflections of QA state.
* **`docs/status/iteration_log.md`** – discovery follow-up ledger kept in sync after each run.
* **`changes/CH-###/seed/REVIEW.md`** – living review digest synthesised from human feedback prior to approvals.
* **`artifacts/ms02/storyboard/summary.md` / `gaps.md`** – governance publication outputs for each scoped execution run.
* **`PROGRESS.md`** – generated summary showing milestones, phase state, and top open concerns.

Each update must include:

* Commit metadata (agent ID, timestamp, policy hash).
* QA validation ID linking to `/audit/`.

---

## 5. Escalation & Concern Handling

* Any agent can log a concern with severity: `info`, `warning`, `critical`.
* Concerns post to Discord and `/audit/concerns.jsonl`.
* PM aggregates and summarizes open items in `PROGRESS.md`.
* Critical concerns trigger `/pause` until acknowledged or resolved.

---

## 6. Progress Tracking

`PROGRESS.md` should include:

* Current phase and iteration number.
* Summary of tasks completed.
* QA status overview (pass %, coverage %, drift).
* List of open and resolved concerns.
* Summary of last human review.

Updates:

* After each QA cycle or agent merge.
* After every human review.
* Daily automated digest posted to Discord.

---

## 7. Metrics & Observability

| Metric             | Source           | Purpose                               |
| ------------------ | ---------------- | ------------------------------------- |
| Test Coverage %    | QA Engine        | Health of test suite                  |
| Reproducibility %  | Regression Tests | Stability measure                     |
| Drift %            | QA Engine        | Detect environment or code drift      |
| Concern Count      | Audit Logs       | Detect instability or workload spikes |
| Mean QA Cycle Time | PM Agent         | Efficiency metric                     |

---

## 8. Governance Summary

* Agents are fully autonomous within policy constraints.
* Human reviews are checkpoint-based, not continuous.
* Documentation and QA artifacts are regenerated automatically.
* Discord and audit logs form the control plane.

---

## 9. Immediate Actions (MS-02)

* [x] Land MS-02 storyboard and align supporting docs (architecture, RACI, requirements, tech stack, traceability).
* [x] Introduce iteration log (`docs/status/iteration_log.md`), loop plan (`loop-plan.json`), and governance summary templates (`artifacts/ms02/storyboard/`).
* [ ] Automate loop-planning prompt → seed generation handshake with audit logging.
* [ ] Implement governance summary publication with skip protection + waiver capture.
* [ ] Extend QA engine to validate doc freshness, loop-plan scope metadata, and review digest updates.
* [ ] Instrument `PROGRESS.md` auto-generation for combined discovery/execution reporting.

---

This workflow ensures that Codexa.ai operates with **low friction**, **high accountability**, and **clear communication**, keeping the architecture, requirements, and testing states synchronized at all times.
