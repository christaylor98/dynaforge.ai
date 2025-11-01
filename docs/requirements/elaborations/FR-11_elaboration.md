---
fr_id: FR-11
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#fr-11-qa-policy-enforcement
  - TRACEABILITY.md#ws-104-qa-policy-enforcement
status: Draft
---

# 🧩 Requirement Elaboration — FR-11

## 1. Summary
Ensure the QA policy engine enforces risk, governance, and maturity thresholds by evaluating Implementer outputs, Change Evaluator notes, TQA metrics, and `/df.*` findings before allowing `CH-###` promotion to HR approval.

## 2. Context & Rationale
Even in the spike we must prove that quality gates are codified and enforced. FR-11 gives QA agents objective criteria derived from `QA_POLICY.yaml`, TQA metrics, and Governance Officer requirements, stopping merges when coverage, risk tiers, `/df.checklist` results, or staged approvals are missing. CR002 adds maturity-aware thresholds, integration with Implementer retention logs, and the requirement that Governance Officer sign-off precedes HR approval.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `qa_policy` | YAML (`QA_POLICY.yaml`) | `risk_tiers:\n  high:\n    min_tests: 3\n    require_go_signoff: true` | Defines thresholds and rules.
| `implementation_report` | Markdown (`docs/IMPLEMENTATION_PLAN.md`) | `- FR-11: tests added TC-FR11-001` | Lists delivered artifacts.
| `change_evaluator_summary` | JSON (`artifacts/phase1/change_evaluator.json`) | `{"risk_tier":"medium","recommended_tests":2}` | Advisory inputs.
| `tqa_metrics` | JSON (`artifacts/phase1/tqa/coverage.json`) | `{"fr_id":"FR-11","required_depth":3,"actual_depth":2}` | Provides risk-tier depth verification.
| `df_checklist_output` | JSON (`artifacts/analyze/df_checklist.json`) | `{"ch_id":"CH-017","qa_status":"pass"}` | Confirms readiness before approvals.
| `test_results` | JUnit XML (`artifacts/phase1/tests/results.xml`) | `<testsuite tests="3" failures="0">` | Evidence of execution.
| `approval_events` | JSONL (`artifacts/phase1/approvals/events.jsonl`) | `{"ch_id":"CH-017","stage":"Governance Officer","decision":"approved"}` | Required for gating order.
| `retention_summary` | JSON (`artifacts/work/CH-017/run-*/summary.json`) | `{"retained":false}` | Ensures retention cleared or justified.

### Edge & Error Inputs
- Missing or malformed `QA_POLICY.yaml` → engine halts promotion, logs error, raises concern, and notifies PM.
- Change Evaluator unavailable → fall back to default risk tier (medium) but flag in audit log and require Governance Officer comment.
- Test results absent → mark requirement `PARTIAL`, block PM from closing milestone, and raise FR-07 concern.
- TQA metrics missing for high risk tier → treat as failure, require Implementer/TQA follow-up.
- `/df.checklist` missing or failing → block verdict until checklist passes.

## 4. Process Flow
```mermaid
flowchart TD
  A[Load qa_policy] --> B[Gather change context (risk tier, maturity, ch_id)]
  B --> C[Compile evidence (tests, tqa metrics, approvals, checklist, retention)]
  C --> D[Evaluate rules per risk tier & maturity level]
  D --> E{All rules satisfied?}
  E -->|Yes| F[Emit PASS verdict + notify PM + Governance Officer]
  E -->|No| G[Emit BLOCK verdict + list gaps + retention instructions]
  G --> H[Raise concern + update traceability + change workspace]
  F --> I[Log decision to audit + status docs]
  H --> I
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| JSON | `artifacts/phase1/qa/verdicts/FR-11.json` with `{risk_tier, maturity, verdict, gaps[]}` | PM, Governance |
| Markdown | `tests/TEST_PLAN.md` status update referencing `CH-###` | QA team, Tester |
| JSONL | `audit/qa_policy.jsonl` decision record including `checklist_hash`, `retained_run_id` | Audit, Compliance |
| Markdown | `changes/CH-###/status.md` appended with QA verdict summary | Governance Officer

## 6. Mockups / UI Views (if applicable)
- `artifacts/phase1/screenshots/qa_policy_cli.md` — CLI view of pass/block verdict.
- `artifacts/phase1/screenshots/qa_gap_report.md` — Table of unmet criteria for demo.
- `artifacts/phase1/screenshots/qa_retention_notice.md` — Example where QA blocks due to retained run.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, individual `CH-###` governed by QA verdict.
- `trace_sections`: `TRACEABILITY.md#fr-11-qa-policy-enforcement`, `TRACEABILITY.md#ws-104-qa-policy-enforcement`, `TRACEABILITY.md#ws-303-qa-policy-engine-enhancements`.
- `artifacts`: `artifacts/phase1/qa/verdicts/`, `TRACEABILITY.md`, `changes/CH-###/status.md`.

## 7. Acceptance Criteria
* [ ] QA engine validates `QA_POLICY.yaml` syntax and logs version hash before evaluation.
* [ ] Verdict references `{fr_id, ch_id, risk_tier, maturity_level, required_tests, actual_tests, checklist_hash, retained_run_id}`.
* [ ] Blocked verdicts automatically raise an FR-07 concern with specific gap details and recommended remediation tasks.
* [ ] PASS verdict requires `df.checklist` success and Governance Officer approval before notifying PM/HR; status docs update within the same orchestration cycle.

## 8. Dependencies
- FR-06 logging for QA decisions, FR-26 traceability, FR-27 retention tracking.
- FR-10 approvals that QA enforces (ensuring GO sign-off), FR-28 `/df.*` commands, FR-30 metrics.
- FR-05 Tester workflows for test evidence, FR-19 TQA metrics.
- WS-104 QA policy enforcement, WS-303 QA policy engine enhancements, WS-302 test synthesizer integration.

## 9. Risks & Assumptions
- Assumes test suite results are available in standardized format (JUnit XML) for parsing; specify fallback.
- Rule changes in `QA_POLICY.yaml` must be versioned; lack of change control could cause drift—enforce change objects for policy edits.
- Risk tier inference depends on Change Evaluator availability; fallback logic must be explicit and recorded in verdict.
- High-risk changes may require manual overrides; engine must capture override rationale and approvals.

## 9.1 Retention Notes
- Verdict must record whether Implementer runs are retained; blocked verdicts should reference retained run folder and reason.
- When retention cleared post-approval, QA logs purge confirmation for FR-27 audit trail.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
