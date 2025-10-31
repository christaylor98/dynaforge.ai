# 🧩 Requirement Elaboration — FR-11

## 1. Summary
Ensure the QA Policy engine enforces risk and governance thresholds during MS-01 by evaluating Implementer outputs, Change Evaluator notes, and maturity rules before allowing promotion.

## 2. Context & Rationale
Even in the spike we must prove that quality gates are codified and enforced. FR-11 gives the Tester and QA agents objective criteria derived from `QA_POLICY.yaml`, stopping merges when coverage, risk tiers, or required approvals are missing. This backs the demo storyline that Dynaforge prevents unsafe changes.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `qa_policy` | YAML (`QA_POLICY.yaml`) | `risk_tiers:\n  high:\n    min_tests: 3` | Defines thresholds and rules. |
| `implementation_report` | Markdown (`docs/IMPLEMENTATION_PLAN.md`) | `- FR-11: tests added TC-FR11-001` | Lists delivered artifacts. |
| `change_evaluator_summary` | JSON (`artifacts/phase1/change_evaluator.json`) | `{"risk_tier":"medium","recommended_tests":2}` | Advisory inputs. |
| `test_results` | JUnit XML (`artifacts/phase1/tests/results.xml`) | `<testsuite tests="3" failures="0">` | Evidence of execution. |
| `approval_events` | JSONL (`artifacts/phase1/approvals/events.jsonl`) | `{"fr_id":"FR-11","decision":"approved"}` | Needed to check gating order. |

### Edge & Error Inputs
- Missing or malformed `QA_POLICY.yaml` → engine halts promotion, logs error, raises concern.
- Change Evaluator unavailable → fall back to default risk tier (medium) but flag in audit log.
- Test results absent → mark requirement `PARTIAL` and block PM from closing milestone.

## 4. Process Flow
```mermaid
flowchart TD
  A[Load qa_policy] --> B[Gather change context (risk tier, maturity)]
  B --> C[Compile evidence (tests, docs, approvals)]
  C --> D[Evaluate rules per risk tier & maturity]
  D --> E{All rules satisfied?}
  E -->|Yes| F[Emit PASS verdict + notify PM]
  E -->|No| G[Emit BLOCK verdict + list gaps]
  G --> H[Raise concern + update traceability]
  F --> I[Log decision to audit]
  H --> I
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| JSON | `artifacts/phase1/qa/verdicts/FR-11.json` | PM, Governance |
| Markdown | `tests/TEST_PLAN.md` status update | QA team, Tester |
| JSONL | `audit/qa_policy.jsonl` decision record | Audit, Compliance |

## 6. Mockups / UI Views (if applicable)
- `artifacts/phase1/screenshots/qa_policy_cli.md` — CLI view of pass/block verdict.
- `artifacts/phase1/screenshots/qa_gap_report.md` — Table of unmet criteria for demo.

## 7. Acceptance Criteria
* [ ] QA engine reads `QA_POLICY.yaml` and validates syntax before evaluation.
* [ ] Verdict references `{fr_id, risk_tier, maturity_level, required_tests, actual_tests}`.
* [ ] Blocked verdicts automatically raise a concern (FR-07) tagged with gap details.
* [ ] PASS verdict triggers PM to update status docs within the same orchestration cycle.

## 8. Dependencies
- FR-06 for logging QA decisions.
- FR-10 for approvals that QA enforces.
- FR-05/Tester workflows for test evidence.
- WS-104 QA policy enforcement, WS-303 future QA automation.

## 9. Risks & Assumptions
- Assumes test suite results are available in a standardized format (JUnit XML) for parsing.
- Rule changes in `QA_POLICY.yaml` must be versioned; lack of change control could cause drift.
- Risk tier inference depends on Change Evaluator availability; fallback logic must be explicit.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-10-30 |
| **Linked Change** | Pending |
