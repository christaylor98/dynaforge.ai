# Test Plan — Phase 0

## Objectives
- Validate audit logging primitives for correctness and schema compliance.
- Exercise interaction stubs and PM agent flows through deterministic scenarios.
- Confirm QA policy parser handles happy path and error conditions.

## Test Strategy
- `pytest` unit coverage for audit logger and parser utilities.
- Manual CLI walkthrough for interaction stub commands.
- Idempotent `make demo` execution logged for regression tracking.

## Test Environments
- Local developer workstation (Python 3.11+).
- Continuous integration pipeline (TBD).

## Entry Criteria
- Repository skeleton established with required modules.
- Dependencies installed and documented.

## Exit Criteria
- All critical tests pass with evidence stored in `artifacts/phase0/`.
- No open high-severity concerns in audit logs.

## Evidence (Latest Run)
- `python3 -m unittest discover -s tests -p 'test_*.py'` — 3 tests passing.
- `python3 -m trace --count --summary --coverdir=artifacts/phase0/trace --module unittest discover -s tests -p 'test_*.py'` — `audit/logger.py` covered at 100%. Summary logged to `artifacts/phase0/trace/coverage_summary.txt`.
