# CH-003 — MS-03 Operating Model Integration

## Summary
Deliver the CR004 operating model by enforcing `.codexa/` scaffolding, publishing the global control-plane bundle, and providing configuration validation tooling and provenance logging across the Codexa workflow.

## Links
- Change Request: `docs/CHANGE_REQUEST_004_operating_model.md`
- Requirement Impact: `docs/CR004_REQUIREMENT_IMPACT.md`
- Milestone: `TRACEABILITY.md` (MS-03)
- Tasks: `backlog/ms03_operating_model_tasks.md`
- Design: `docs/design/MS03_operating_model_spec.md`

## Objectives
1. Implement FR-42–FR-44 and associated updates to FR-01/FR-02/FR-06/FR-32/FR-38/FR-39.
2. Ship `codexa doctor config` with automated precedence tests and telemetry.
3. Ensure audit/status artifacts record configuration lineage for every run.
4. Provide migration guidance and linting so legacy repos adopt `.codexa/` without drift.

## Success Criteria
- `codexa doctor config` passes in CI and blocks merges on failures.
- `.codexa/` lint + migration tooling validated with sample repo evidence.
- Global control-plane bundle versioned and hashed; provenance stored in audit logs.
- Discovery manifests and maturity metadata reflect new locations and provenance.
