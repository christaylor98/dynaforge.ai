# MS-03 Operating Model Integration — Task Breakdown

## Scope Reference
- Change Request: `docs/CHANGE_REQUEST_004_operating_model.md`
- Requirement Impact: `docs/CR004_REQUIREMENT_IMPACT.md`
- Milestone Anchor: `TRACEABILITY.md` (MS-03)
- Requirements: FR-01, FR-02, FR-06, FR-32, FR-38, FR-39, FR-42, FR-43, FR-44

## WS-10 Operating Model Scaffolding (FR-42)
- [x] Author `.codexa/` directory contract (structure, required files, permitted extensions).
- [x] Implement `codexa init --operating-model` scaffold command.
- [ ] Add schema lint helper/CI guard verifying `.codexa/` compliance.
- [ ] Build Spec-Kit migration helper (`codexa migrate spec-kit`) with dry-run mode.
- [ ] Update documentation (`.codexa/README.md` template, `docs/CHANGE_REQUEST_004_operating_model.md` appendix).
- [ ] Record acceptance evidence for TC-FR42-001 (lint output, failing sample, passing sample).

## WS-10 Operating Model Scaffolding (FR-43)
- [ ] Define `~/.config/codexa/` bundle structure (`core.yaml`, `templates/`, `policies/`, version metadata).
- [ ] Implement semantic versioning + change log generator for global bundle.
- [ ] Wire provenance hashing routine (hash of bundle + project override) for CLI/audit use.
- [ ] Provide installer/sync command (`codexa control-plane sync`) with offline cache support.
- [ ] Add samples + documentation (`docs/global_control_plane.md`) and link from `.codexa/README.md`.
- [ ] Capture TC-FR43-001 evidence (version bump + automated validation output).

## WS-207 Interaction CLI Extensions (FR-44 + FR-28)
- [ ] Draft CLI UX for `codexa doctor config` (flags, exit codes, telemetry payload).
- [ ] Implement configuration resolver diagnostics (project/global/hybrid/override scenarios).
- [ ] Extend existing `/df.*` commands to record configuration lineage hints when available.
- [ ] Write automated tests covering precedence matrix + failure handling (TC-FR44-001).
- [ ] Emit structured JSON report for audit ingestion + developer consumption.
- [ ] Update CLI docs, help text, and quickstart guides.

## WS-206 Change Records & Audit Extensions (FR-06 updates)
- [ ] Extend audit schema to include `{config_root, extends_from, template_hash}`.
- [ ] Update logging middleware across PM, DA, GO agents to populate new fields.
- [ ] Backfill status documentation templates to surface configuration lineage.
- [ ] Add migration note for historical logs (optional backfill strategy or annotation).
- [ ] Prove TC-FR06-002 with new schema sample + CI validation.

## WS-304 Maturity Metadata & Guides (FR-32 update)
- [ ] Relocate canonical metadata to `.codexa/project_metadata.yaml`; maintain mirrored `PROJECT_METADATA.md`.
- [ ] Introduce validation ensuring mirror sync and provenance logging.
- [ ] Update `PROCESS_MATURITY_GUIDE.md` and RACI notes to reference new location.
- [ ] Adjust agent utilities (PM, GO, QA) to consume `.codexa/project_metadata.yaml`.
- [ ] Record TC-FR32-001 evidence after relocation + validation run.

## WS-09 Discovery Foundations (FR-38/FR-39 updates)
- [ ] Ensure discovery outputs land in `.codexa/manifests/` with `extends` metadata.
- [ ] Update System Model Graph projections to log configuration provenance.
- [ ] Validate manifest schema changes + refresh iteration log references.
- [ ] Capture TC-FR38-001 / TC-FR39-001 evidence with new layout.

## Cross-Cutting Tasks
- [ ] Update traceability, RACI, architecture, tech stack docs with final implementation details.
- [ ] Prepare MS-03 demo checklist (lint run, doctor output, audit log sample, metadata inspection).
- [ ] Collect risk mitigations (fallback behaviour when `.codexa/` missing, global bundle unavailable).
- [ ] Define roll-forward/rollback strategy for configuration schema changes.
