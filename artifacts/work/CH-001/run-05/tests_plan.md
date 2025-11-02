# Test Plan — CH-001 Execute Handoff

## Overview
- Change: `CH-001`
- Phase: 0 — Foundation
- Seed: `MS01-P0-2025-11-02`
- Target Test Cases: TC-FR01-001, TC-FR01-002, TC-FR06-001, TC-FR08-001

## Environment
- `PYTHONPATH` includes project root (default when running from repo).
- `Codexa_SEED=MS01-P0-2025-11-02`
- `Codexa_PHASE=0`

## Commands
| Test Case | Command |
| --- | --- |
| TC-FR01-001 | `pytest tests/test_agents_workflow.py::ProjectManagerIntegrationTest::test_run_writes_documents_and_audit_handoff` |
| TC-FR01-002 | `pytest tests/test_agents_workflow.py::Phase1OrchestratorIntegrationTest::test_orchestrate_writes_summary_and_expected_artifacts` |
| TC-FR06-001 | `pytest tests/test_logger.py` |
| TC-FR08-001 | `pytest tests/test_interaction_stub.py` |

## Additional Checks (Pre-Validation)
1. Record deterministic checksum for demo bundle handoff log  
   `sha256sum artifacts/phase0/demo/2025-11-02/handoff.jsonl > artifacts/work/CH-001/run-05/demo_checksum.txt`
2. Verify audit JSONL files include CH-001 metadata  
   `python3 - <<'PY' > artifacts/work/CH-001/run-05/audit_validation.json\nimport json\nimport pathlib\nimport sys\n\npaths = [\n    pathlib.Path(\"audit/handoff_ms01_phase0.jsonl\"),\n    pathlib.Path(\"audit/handoff.jsonl\")\n]\nresults = {}\nfor path in paths:\n    records = []\n    with path.open(encoding=\"utf-8\") as handle:\n        for line in handle:\n            try:\n                data = json.loads(line)\n            except json.JSONDecodeError:\n                continue\n            if data.get(\"metadata\", {}).get(\"change_id\") == \"CH-001\":\n                records.append(data)\n    results[str(path)] = len(records)\n    if not records:\n        raise SystemExit(f\"Missing CH-001 metadata in {path}\")\n\njson.dump(results, sys.stdout, indent=2)\nPY`
3. Confirm docs reference the refreshed change context  
   `python3 - <<'PY' > artifacts/work/CH-001/run-05/doc_reference_check.txt\nimport pathlib\npaths = [\n    pathlib.Path(\"docs/PROJECT_OVERVIEW.md\"),\n    pathlib.Path(\"docs/PROJECT_DETAIL.md\"),\n    pathlib.Path(\"docs/IMPLEMENTATION_PLAN.md\"),\n    pathlib.Path(\"docs/VERSION_CONTROL.md\")\n]\nmissing = []\nfor path in paths:\n    text = path.read_text(encoding=\"utf-8\")\n    if \"CH-001\" not in text:\n        missing.append(str(path))\nif missing:\n    raise SystemExit(f\"CH-001 reference missing in: {', '.join(missing)}\")\nprint(\"doc-references-ok\")\nPY`
4. Validate Phase 0 command log entries exist for `/status`, `/clarify`, `/approve`  
   `python3 - <<'PY' > artifacts/work/CH-001/run-05/command_log_check.txt\nimport json, pathlib\npath = pathlib.Path(\"audit/commands.jsonl\")\nrequired = {\"/status\", \"/clarify\", \"/approve\"}\nobserved = set()\nwith path.open(encoding=\"utf-8\") as handle:\n    for line in handle:\n        data = json.loads(line)\n        if data.get(\"metadata\", {}).get(\"change_id\") == \"CH-001\":\n            observed.add(data.get(\"command\"))\nmissing = required - observed\nif missing:\n    raise SystemExit(f\"Missing CH-001 command entries for: {', '.join(sorted(missing))}\")\nprint(\"command-log-ok\")\nPY`

## Artifacts to Capture
- Consolidated results: `tests/results/CH-001.json`
- QA summary entry in `QA_REPORT.md`
- Audit trail excerpt appended to `audit/commands.jsonl` for test-triggered commands.
- Demo checksum: `artifacts/work/CH-001/run-05/demo_checksum.txt`
- Audit validation output: `artifacts/work/CH-001/run-05/audit_validation.json`
- Documentation reference log: `artifacts/work/CH-001/run-05/doc_reference_check.txt`
- Command log verification: `artifacts/work/CH-001/run-05/command_log_check.txt`

## Notes
- Execute commands in listed order to mirror PM → Designer → Implementer → Tester loop.
- If any command fails, file a concern via `/clarify CH-001` and append context to `changes/CH-001/status.md`.
