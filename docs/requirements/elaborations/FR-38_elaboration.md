---
fr_id: FR-38
ch_refs:
  - CH-003
trace_links:
  - TRACEABILITY.md#fr-38-discovery-pipeline-artifacts
status: Draft
---
# 🧩 Requirement Elaboration — FR-38

## 1. Summary
Deliver a deterministic discovery pipeline (CLI + agents) that scans any repository and emits repo-tracked manifests describing structure, change zones, and inferred intent across quick, deep, and code-only modes.

## 2. Context & Rationale
- Codexa must bootstrap understanding from existing systems before planning change (CR003 manifesto).
- Prior workflows assume documentation or tests; this pipeline guarantees a canonical starting point for million-line monoliths down to empty repos.
- Discovery outputs unblock RA/IA agents and feed traceability, milestones, and change seeds.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| repo_path | filesystem path | `.` | Root of repository under analysis. |
| mode | enum (`quick`, `deep`, `code-only`) | `code-only` | Determines scan depth and heuristics. |
| focus | optional glob / module list | `services/trading_engine` | Limits analysis surface for targeted discovery. |
| options | CLI flags | `--languages python,rust` | Allows overrides for language detection, ignore patterns, concurrency. |

### Edge & Error Inputs
- Non-existent path → emit CLI error `DF_DISCOVERY_001` and do not write manifests.
- Repos larger than configured limits → produce partial manifest with warning `partial: true` + skipped paths section.
- Unsupported languages → list under `languages_unresolved` and continue scanning remaining files.

## 4. Process Flow
```mermaid
flowchart TD
  A[Invoke codexa discover] --> B[Detect languages / repo metrics]
  B --> C1[Quick Scan (summaries only)]
  B --> C2[Deep Scan (full graph)] 
  B --> C3[Code-only fallback]
  C1 --> D[Generate system_manifest.yaml]
  C2 --> D
  C3 --> D
  D --> E[Compute change_zones.md]
  D --> F[Infer intent_map.md]
  E --> G[Persist manifests + hashes]
  F --> G
  G --> H[Update System Model Graph YAML]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| YAML | `analysis/system_manifest.yaml` | PM, RA, DA agents |
| Markdown | `analysis/change_zones.md` | IM, IA, PM |
| Markdown | `analysis/intent_map.md` | RA, Designer |
| JSON (optional) | `artifacts/discovery/run-001/report.json` | Analytics (coverage metrics) |

## 6. Mockups / UI Views
- CLI help snapshot: `artifacts/mockups/FR-38/codexa_discover_help.png`
- Example manifest snippet: `artifacts/mockups/FR-38/system_manifest_sample.yaml`

## 6.1 Change & Traceability Links
- change_refs: `CH-003` (Discovery initiative main thread).
- trace_sections: `TRACEABILITY.md#ws-09-discovery-foundations`, `TRACEABILITY.md#fr-38-discovery-pipeline-artifacts`.
- artifacts: `docs/archive/CHANGE_REQUEST_003_discovery.md`, `docs/REQUIREMENTS_1_3.md`.

## 7. Acceptance Criteria
- [ ] `codexa discover --depth quick` generates manifest + change_zones + intent_map within 2 minutes for repos ≤ 2000 files.
- [ ] `codexa discover --mode code-only` succeeds when docs/tests absent and flags fallback mode in manifest metadata.
- [ ] Every manifest includes `generated_at`, `commit_sha`, `discovery_mode`, and `hash` for audit replay.
- [ ] Manifests tracked in Git under `analysis/` and linked in `TRACEABILITY.md`.
- [ ] Discovery runs update System Model Graph projections (FR-39) or emit warning if graph refresh fails.

## 8. Dependencies
- FR-39 (System Model Graph YAML projections).
- FR-41 (Understanding coverage metrics).
- Tooling stack: tree-sitter, tokei, radon, pygount, Git metadata fetch.

## 9. Risks & Assumptions
- Large repos may require chunked execution; ensure streaming writes to avoid memory spikes.
- Requires sandboxing to prevent execution of arbitrary code (stay within static analysis).
- Assumes repository is locally available; remote SCM integration tracked separately.

## 9.1 Retention Notes
- Store discovery run metadata under `artifacts/discovery/` for 30 days; mark `--retain` when capturing evidence for audits or demos.

## 10. Review Status
| Field | Value |
| --- | --- |
| **Status** | Draft |
| **Reviewed By** | _Pending_ |
| **Date** | 2025-11-04 |
| **Linked Change** | CH-003 |
