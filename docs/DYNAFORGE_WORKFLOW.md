# 🧩 DYNAFORGE_WORKFLOW.md — Autonomous Coding Workflow

## 1. Purpose

Define the operating workflow for **Dynaforge.ai**, focusing on maintaining a high degree of autonomy while ensuring architectural, requirements, and testing documentation remain synchronized and accurate.

This workflow minimizes human intervention — the system must self-report, self-correct, and surface concerns rather than require manual oversight.

---

## 2. Workflow Principles

1. **Autonomy First** – Agents should drive progress end-to-end, only escalating when policies or confidence thresholds are violated.
2. **Transparency Over Intervention** – Human visibility through dashboards and Discord is preferred to direct commands.
3. **Source of Truth Documents** – `ARCHITECTURE.md`, `REQUIREMENTS.md`, and `TEST_PLAN.md` are always current and regenerated as part of QA.
4. **Progress as a Deliverable** – `PROGRESS.md` acts as the live narrative of system evolution, updated automatically.
5. **Audit and Evidence-Based Validation** – Every step leaves verifiable artifacts in `/audit/`.

---

## 3. Core Workflow Loop

### 3.1 Autonomous Loop

```
[Designer] → [Implementer] → [Tester] → [QA Engine] → [PM]
          ↘───────────────Audit + QA Reports──────────────↙
```

1. **Designer** updates or refines `ARCHITECTURE.md` when design changes occur.
2. **Implementer** generates or updates code.
3. **Tester** updates `TEST_PLAN.md` and runs regression + validation tests.
4. **QA Engine** verifies metrics and regenerates:

   * `QA_REPORT.md`
   * `REQUIREMENTS_STATUS.md`
   * `PROGRESS.md`
5. **PM Agent** reviews the artifacts, merges if gates pass, or escalates to Human if not.

---

### 3.2 Human-in-the-Loop Checkpoints

The Human only reviews:

* New or revised project plan summaries.
* Architectural or requirements changes tagged as `impact: high`.
* QA or performance failures beyond policy thresholds.
* Phase promotions or milestone reviews.

Commands available via Discord:

```
/status      # Current phase, test status, active concerns
/clarify X   # Request context from agent X
/promote     # Approve phase promotion
/pause       # Halt the workflow loop for investigation
/resume      # Resume automated loop
```

---

## 4. Continuous Documentation Flow

* **`ARCHITECTURE.md`** – auto-updated when structure or API contracts change.
* **`REQUIREMENTS.md`** – updated with coverage, completion %, and traceability.
* **`TEST_PLAN.md` / `TEST_RESULTS.md`** – live reflections of QA state.
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

## 9. Immediate Actions (Phase 0–1)

* [x] Provide Phase 0 demo workflow via `make demo`, `make audit`, and `make clean` (artifacts stored under `artifacts/phase0/demo`).
* [ ] Implement `PROGRESS.md` auto-generation pipeline.
* [ ] Extend QA engine to validate doc freshness and sync.
* [ ] Integrate concern summarization into Discord notifier.
* [ ] Create daily digest command `/digest` to post key metrics.
* [ ] Set thresholds for doc staleness (e.g., >48h triggers concern).

---

This workflow ensures that Dynaforge.ai operates with **low friction**, **high accountability**, and **clear communication**, keeping the architecture, requirements, and testing states synchronized at all times.
