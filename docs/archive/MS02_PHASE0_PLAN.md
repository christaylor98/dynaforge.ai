# MS-02 Phase 0 Plan — Discovery Foundations

## 1. Purpose & Scope
Establish the minimum-but-complete discovery foundation for Milestone MS-02. This phase delivers scaffolding that makes `system_manifest.yaml`, `change_zones.md`, and `intent_map.md` first-class artifacts even before the automated discovery pipeline lands. The goal is to unblock downstream phases by providing configuration contracts, schema baselines, governance hooks, and demo collateral that prove the flow end-to-end.

## Reference Documents
- `design/MS-02_storyboard.md` — canonical journey for discovery → seed → governance.
- `docs/ARCHITECTURE.md` — layered architecture with discovery/understanding context.
- `docs/REQUIREMENTS_1_3.md` — FR-38/FR-39/FR-41 definitions driving discovery outputs.
- `TRACEABILITY.md` — current workstream statuses (WS-09, WS-110, WS-201).
- `docs/archive/PHASE0_PLAN.md` — template from MS-01 Phase 0 (structure + expectations).
- `scripts/ms02_dry_run.py` — existing dry-run generator used for demos/onboarding.
- `analysis/system_manifest.yaml` — bootstrap manifest aligned with FR-38.

## 2. Workstreams & Tasks

| ID | Workstream | Key Tasks | Primary Owner | Dependencies | Validation Anchor |
| -- | ---------- | --------- | ------------- | ------------ | ----------------- |
| WS-D1 | Discovery Config Skeleton | Draft `docs/discovery/config.yaml`, document supported modes, add TODO guards in CLI stubs. | Discovery Analyzer (delegated to Implementer) | None | Config template committed; dry run references resolved. |
| WS-D2 | Manifest Schema & Repository Contracts | Define manifest schema docs, seed `analysis/system_manifest.yaml`, add trace hooks to `TRACEABILITY.md`. | Discovery Analyzer + Governance Officer | WS-D1 | Schema doc + manifest diff reviewed; trace links updated. |
| WS-D3 | Iteration Log & Follow-up Loop | Harden `docs/status/iteration_log.md`, ensure follow-ups sync to `artifacts/ms02/storyboard/gaps.md`, add guidelines for humans. | Project Manager | WS-D2 | Iteration log template validated; reconciliation script instructions captured. |
| WS-D4 | Governance & Traceability Alignment | Update `TRACEABILITY.md`, `docs/PROJECT_OVERVIEW.md`, and `AGENTS_RACI.md` to reference discovery artifacts and responsibilities. | Governance Officer | WS-D2 | Traceability diff showing FR-38/41 evidence paths. |
| WS-D5 | Demo & Dry-Run Refresh | Extend `scripts/ms02_dry_run.py` to use new config + schema, wire the production `codexa discover` CLI (backed by `scripts/discovery_bootstrap.py`) for automated manifest generation (including repository insights + blast radius), capture audit handoff for discovery stage, publish walkthrough README. | Implementer + Tester | WS-D1–WS-D4 | Demo replay documented; audit entry recorded. |

## 3. Validation Plan

| Workstream | Verification Steps | Owner | Evidence Artifact |
| ---------- | ------------------ | ----- | ----------------- |
| WS-D1 | Run `python scripts/ms02_dry_run.py --help`; ensure config path present and template is readable. | Tester | `artifacts/ms02/phase0/config_validation.md` |
| WS-D2 | Validate manifest schema against sample using `yamllint`/manual review; confirm traceability rows link to manifest hashes. | Governance Officer | `analysis/system_manifest.yaml`, `docs/requirements/elaborations/FR-38_elaboration.md` |
| WS-D3 | Simulate follow-up resolution; verify iteration log + gaps stay in sync. | Project Manager | `artifacts/ms02/phase0/iteration_sync.log` |
| WS-D4 | Run `grep -n "system_manifest"` across repo; confirm governance docs reference new artifacts. | Governance Officer | `artifacts/ms02/phase0/traceability_check.txt` |
| WS-D5 | Execute dry run + bootstrap generation; confirm audit log entry `handoff_discovery.jsonl` created. | Tester | `artifacts/ms02/phase0/dry_run_report.md` |

## 4. Exit Criteria
- `docs/discovery/config.yaml` committed with documented defaults and guardrails.
- `analysis/system_manifest.yaml`, `analysis/change_zones.md`, and `analysis/intent_map.md` exist with Phase 0 scaffolding linked to traceability.
- Iteration log + gaps file workflow documented and validated.
- Governance docs updated with discovery responsibilities and evidence references.
- Dry-run/demo instructions produce reproducible artifacts and capture discovery handoff in audit logs.
- No open Phase 0 concerns; outstanding follow-ups either resolved or tracked with mitigation.

## 5. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Discovery config drifts from future CLI implementation. | Medium | High | Treat template as contract; document compatibility expectations; add TODO markers to revisit once CLI lands. |
| Manual manifest falls behind reality before automation. | Medium | Medium | Capture update checklist in README; require manifest review before Phase 1 kickoff. |
| Follow-up reconciliation fails without automation. | Low | Medium | Provide explicit manual steps in plan; add assertions to dry-run script. |
| Governance docs omit new evidence paths. | Low | High | Traceability review required before exit; include checklists in WS-D4 tasks. |

## 6. Timeline & Checkpoints
- **Day 1**: WS-D1 + WS-D2 scaffolding (config, manifest schema, trace hooks) drafted and reviewed.
- **Day 2**: WS-D3 follow-up loop hardened; documentation updates for governance alignment.
- **Day 3**: WS-D5 dry-run refresh executed; audit entries and demo collateral captured.
- **Day 4**: Buffer for review, remediation, and human approval.

## 7. Approvals & Governance
- Human PM signs off on this plan (`docs/MS02_PHASE0_PLAN.md`) before execution (`✅ Approved by Human <date>`).
- Governance Officer validates traceability and evidence updates post-execution.
- Upon completion, Project Manager logs Phase 0 close-out summary in `docs/status/iteration_log.md` and updates `TRACEABILITY.md` statuses (WS-D1–WS-D5).

`✅ Approved by Human 2025-11-03`
