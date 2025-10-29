Ah — got it. You don’t want the *workflow that Overlord will run later*; you want the *workflow for us building Overlord itself*.
So this will describe **how we (human + agent + code) will build, test, and iterate the Code Overlord project** — the development roadmap, not its runtime.

Here’s how we can structure that:

---

### 🧭 CODE_OVERLORD_PROJECT_WORKFLOW.md — Development Plan

#### 1. Purpose

Establish a practical, low-friction workflow for building and validating the Code Overlord framework itself — defining phases, testing strategy, review cadence, and how we surface progress and issues.

---

#### 2. Guiding Principles

1. **Small, Testable Increments** – build and validate one subsystem at a time.
2. **Tight Feedback Loops** – each stage must be measurable (unit tests, metrics, or prototype demo).
3. **Human ≠ Bottleneck** – human checkpoints exist only for architecture validation, safety, and direction shifts.
4. **Artifacts as Proof** – every milestone outputs a concrete file: spec, code, or QA report.
5. **Audit Everything** – all actions, merges, and reviews logged and traceable.

---

#### 3. Phase Breakdown

| Phase                         | Focus                                           | Deliverables                                  | Review Trigger                            |
| ----------------------------- | ----------------------------------------------- | --------------------------------------------- | ----------------------------------------- |
| **P0 – Bootstrapping**        | Repo skeleton, documentation, audit schema      | `CODE_OVERLORD.md`, `logger.py`, Discord mock | Human confirms structure + audit works    |
| **P1 – Core Agents**          | PM, Designer, Implementer, Tester base classes  | Basic handoff chain, `audit/` records         | Demo run shows handoff + logging          |
| **P2 – QA Engine**            | Policy reader, test executor, metrics collector | `QA_POLICY.yaml`, `QA_REPORT.md`              | Metrics reproducible, 1st end-to-end pass |
| **P3 – GitOps Integration**   | Auto-commit, merge logic, audit merge events    | `gitops/` scripts, merge logs                 | Merge succeeds + rollback test passes     |
| **P4 – Discord Bridge**       | Real notification + command interface           | Live `/status`, `/clarify`                    | Human review of event accuracy            |
| **P5 – Autonomous Loop Demo** | Combine all agents; continuous QA cycle         | Recorded full loop log + doc sync             | Human review + milestone tag `v0.1`       |

---

#### 4. Testing Strategy

| Layer                 | Tooling                                    | Validation                                               |
| --------------------- | ------------------------------------------ | -------------------------------------------------------- |
| **Unit Tests**        | `pytest`                                   | 90 %+ coverage for core functions                        |
| **Integration Tests** | Python harness simulating full agent cycle | Must reproduce identical audit logs twice                |
| **System Tests**      | End-to-end dry-run (`make demo`)           | QA gates all green, Discord mock receives 3+ event types |
| **Regression**        | Rerun identical seed + data                | Logs and metrics must match                              |
| **Manual Review**     | Human runs `/status`, `/clarify`           | Confirms visibility + correctness                        |

Every phase adds tests to `tests/` and updates `TEST_PLAN.md` + `TEST_RESULTS.md`.

---

#### 5. Review & Approval Points

| Stage                    | Reviewer | Criteria                                  |
| ------------------------ | -------- | ----------------------------------------- |
| Architecture Sketch (P0) | Human    | Folder + interface layout accepted        |
| End of P1                | Human    | Agents run sequentially without errors    |
| End of P2                | Human    | QA gates correctly accept/reject          |
| End of P4                | Human    | Discord interaction validated             |
| Phase Promotion          | Human    | QA Report clean, docs synced, tag created |

All reviews summarized in `PROGRESS.md` with ✅/⚠️ status lines.

---

#### 6. Progress Tracking

`PROGRESS.md` (auto-updated by PM script):

```
## Sprint Summary – Phase 2
Status: ✅ QA Engine implemented
Coverage: 86 %
Reproducibility: 98 %
Open Concerns: 1 (discord latency)
Next Step: Integrate GitOps merge
```

Daily digest pushed to Discord; weekly human note appended manually.

---

#### 7. Issue & Concern Escalation

* Agents raise `concern.json` entries → Discord `#build-alerts`.
* Critical build/test failures auto-pause pipeline.
* Human responds `/resolve <id>` after fix.
* PM posts “return to normal” notice and resumes loop.

##### Audit Schema Addendum
- **Handoff entries** append to `audit/handoff.jsonl` via `AuditLogger.log_handoff()`. Required keys: `record_type="handoff"`, `schema_version`, ISO-8601 `timestamp`, `phase`, `from_agent`, `to_agent`, `summary`. Optional lists `artifacts` and `concerns`, plus free-form `metadata`.
- **Concern entries** append to `audit/concerns.jsonl` via `AuditLogger.log_concern()`. Required keys: `record_type="concern"`, `schema_version`, ISO-8601 `timestamp`, `phase`, `raised_by`, `severity` (`low|medium|high|critical`), and `message`. Optional `resolution` and structured `metadata`.
- All audit artifacts follow JSON Lines formatting; each line is a self-contained record signed with schema version `0.1.0`.

---

#### 8. Testing Environments

| Environment           | Purpose                               |
| --------------------- | ------------------------------------- |
| **Local (Docker)**    | Dev + unit tests                      |
| **CI (GitHub/Gitea)** | Full integration & QA                 |
| **Stage (Sandbox)**   | End-to-end demo with Discord + GitOps |

---

#### 9. Success Metrics

* 100 % reproducible builds.
* < 15 min QA cycle time.
* 0 manual merges during phases P1–P4.
* Documentation sync lag < 1 commit.
* One human command (`/promote`) per phase.

---

#### 10. Phase 0 Immediate Next Steps

1. Create minimal working repo + folder tree.
2. Implement logger + `audit.jsonl` writer.
3. Add Discord mock + `/status`.
4. Write skeleton agents (no logic yet).
5. Run first dry-loop test.
6. Human verifies audit entries and approves Phase 1 start.

---
