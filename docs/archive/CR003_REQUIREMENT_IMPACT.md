# CR003 Requirement Impact & Clarifications

## Context
- Change request `docs/archive/CHANGE_REQUEST_003_discovery.md` pivots Codexa toward an understanding-first workflow where discovery artifacts and a System Model Graph become the foundation for every change.
- New CLI commands (`codexa discover`, `codexa summarize`, `codexa suggest-change-zones`) and discovery agents must generate repeatable manifests even when only raw code is available.
- Discovery outputs culminate in a persistent System Model Graph (`system_model.db` + YAML projections) that feeds planning, implementation, testing, and documentation.

## Updated Requirements
| Requirement ID | Current Focus | Required Update from CR003 | Effort (est.) | CR003 Source |
| --- | --- | --- | --- | --- |
| FR-01 Project Manager | Orchestrates multi-agent change loop with maturity awareness. | Insert a discovery pre-flight that ensures `system_manifest.yaml` and `change_zones.md` exist before workstream decomposition; trigger System Model Graph refreshes and surface discovery mode (`code-only`, `deep`) in run metadata. | Medium | Operating Model → Integration with Codexa Workflow. |
| FR-02 Status Documentation | Keep `PROJECT_OVERVIEW.md` / `PROJECT_DETAIL.md` aligned with current change state. | Embed discovery outputs (latest manifest hash, change zone summaries, understanding coverage) and reference the Understanding & Evolve manifesto/tagline in hero docs. | Low-Medium | Intent, Strategic Objectives, Near-Term Deliverables. |
| FR-06 Structured Handoffs & Audit Trails | Capture agent handoffs with rich metadata. | Append discovery artifact references (`analysis/*` paths, model graph version) to audit entries; log whether code-only fallback was used and record CLI command options. | Medium | Operating Model → Integration; Code-Only Mode. |
| FR-13 Status Snapshots | Provide status dashboards with key delivery metrics. | Report understanding coverage, discovery freshness timestamps, and change readiness heatmap excerpts alongside existing maturity metrics. | Medium | Strategic Objectives; Near-Term Deliverables. |
| FR-15 Requirements Analyst | Monitors requirement deltas and traceability. | Consume System Model Graph intent nodes to update FR/WS links; ensure new discovery artifacts auto-link into traceability evidence. | Medium | System Model Graph; Near-Term Deliverables. |
| FR-16 Impact Assessor | Quantifies downstream effects of requirement changes. | Leverage change readiness heatmap and discovery metrics when scoring impacts; include discovery artifacts in `IMPACT_REPORT.md`. | Medium | Code-Only Mode; Near-Term Deliverables. |

## New Requirements
| Proposed ID | Requirement Summary | Primary Owner | Effort (est.) | Motivation from CR003 |
| --- | --- | --- | --- | --- |
| FR-38 | Provide a discovery pipeline (agents + CLI) that generates `system_manifest.yaml`, `change_zones.md`, and `intent_map.md` across quick/deep and code-only modes. | Analyzer / Platform | High | Operating Model layers; CLI commands. |
| FR-39 | Maintain a persistent System Model Graph (`system_model.db` + projections) that synchronizes code structure, intent, requirements, tests, and risks for downstream agents. | Platform Architecture | High | System Model Graph section. |
| FR-40 | Generate Change Seeds with manifests, baseline tests, and context slices via `codexa seed <zone> <mission>`; treat seeds as canonical starting points for change journeys. | Implementer / Seed Planner | Medium-High | Change Seed Layer; Near-Term Deliverables. |
| FR-41 | Instrument understanding coverage and change readiness metrics, surfacing them via CLI status and documentation dashboards. | PM / Analytics | Medium | Strategic Objectives; Near-Term Deliverables. |

## Effort Notes
- High-effort items (FR-38, FR-39) require new agent tooling, persistence layers, and schema alignment across the platform.
- Medium updates introduce new metadata and reporting but can piggyback on existing traceability/audit infrastructure.
- Documentation refresh (FR-02) depends on manifesto delivery but is otherwise straightforward once discovery artifacts exist.

## Suggested Refinements
- Pilot discovery pipeline on a representative large, undocumented repo to validate code-only mode before general release.
- Establish versioning strategy for `system_model.db` snapshots so audit logs can reference immutable hashes.
- Iterate understanding coverage metrics with analytics stakeholders to balance signal vs. noise before hard requirements.

## Clarification Responses
1. **Discovery refresh cadence** — Leave cadence to the adopting team so it aligns with their workflow (per-change, nightly, or manual refresh as needed).
2. **System Model Graph storage** — Canonical truth must remain YAML projections versioned in-repo. No database files are tracked; agents may maintain ephemeral local caches only.
3. **Understanding coverage baseline** — Start with the percentage of files/modules that have both structure and intent maps. Large codebases may target a focused subset initially, with refinement over time.
4. **Change Seed scaffolding** — Roll out language support in waves, beginning with common languages and expanding iteratively.
5. **Manifest history** — Preserve historical manifests per change to capture system evolution and contextualize decisions.
