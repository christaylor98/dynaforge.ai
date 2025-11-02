# Test Plan — CH-002 Validate Stage

## Targets
- TC-FR01-002: Phase 1 orchestrator integration test.
- TC-FR07-001 (integration): Concern lifecycle raise/update/resolve.
- TC-FR11-002: QA enforcement gating.
- Status snapshot verification (new tooling).

## Environment
- `Codexa_SEED=MS01-P1-2025-11-03`
- Ensure `pipelines/qa_enforcer.py`, `pipelines/status_snapshot.py` executable.

## Commands
| Purpose | Command |
| --- | --- |
| Orchestrator integration | `python3 -m unittest tests.test_agents_workflow.Phase1OrchestratorIntegrationTest` |
| Concern lifecycle | `python3 -m unittest tests.test_concern_tools` |
| QA enforcement evaluation | `python3 pipelines/qa_enforcer.py --policy QA_POLICY.yaml --metrics artifacts/work/CH-002/run-03/qa_metrics.json --results tests/results/CH-002.json --change-id CH-002 --output artifacts/work/CH-002/run-03/qa_enforcement.json` |
| Status snapshot check | `python3 pipelines/status_snapshot.py changes/CH-002/status.md --output artifacts/phase1/status/snapshot-2025-11-02.json` |

## Evidence to Capture
- Append test results to `tests/results/CH-002.json`.
- Update `docs/QA_REPORT.md` with validation summary.
- Attach snapshot diff in Package stage.

## Notes
- If QA enforcement fails, file FR-07 concern and note remediation steps.
