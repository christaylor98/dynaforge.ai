---
fr_id: FR-41
ch_refs:
  - CH-003
trace_links:
  - TRACEABILITY.md#fr-41-understanding-coverage-readiness-metrics
status: Draft
---
# 🧩 Requirement Elaboration — FR-41

## 1. Summary
Instrument understanding coverage and change readiness metrics derived from discovery artifacts and surface them through CLI status, dashboards, and documentation while preserving historical manifest snapshots per change.

## 2. Context & Rationale
- Discovery outputs (FR-38, FR-39) need a quantified signal to show progress in comprehension, not just artifact existence.
- Stakeholders require quick insight into how much of the system is mapped before approving changes.
- Metrics guide IA/PM prioritization and feed governance decisions (traceability, risk).

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| discovery_manifests | YAML/MD | `analysis/system_manifest.yaml` | Basis for coverage calculations. |
| system_model_graph | YAML | `analysis/system_model/components.yaml` | Provides node counts, relationships. |
| focus_scope | optional list | `["services/trading_engine", "dashboard"]` | Define subset for targeted coverage. |
| change_history | YAML/JSON | `analysis/manifest_history.yaml` | Tracks previous runs for trend metrics. |

### Edge & Error Inputs
- No discovery manifests → return coverage `0%` with status `stale`.
- Invalid focus scope → warn and default to entire repo.
- Missing historical data → compute point-in-time metrics only, mark trend as `n/a`.

## 4. Process Flow
```mermaid
flowchart TD
  A[Collect discovery + graph data] --> B[Normalize component list]
  B --> C[Compute coverage metrics (structure, intent, tests)]
  C --> D[Assess change readiness heatmap]
  D --> E[Write metrics snapshot YAML + Markdown]
  E --> F[Update /status CLI + dashboards]
  F --> G[Archive metrics in manifest history]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| YAML | `analysis/metrics/understanding_coverage.yaml` | Analytics Lead, PM |
| Markdown | `docs/status/understanding_snapshot.md` | Stakeholders, HR |
| CLI | `/status` response including `coverage: 68%`, `readiness: high` | Operators |
| JSON | `analysis/metrics/heatmap.json` | Dashboards, IA agent |

## 6. Mockups / UI Views
- Sample CLI output screenshot: `artifacts/mockups/FR-41/status_cli.png`
- Dashboard widget mockup: `artifacts/mockups/FR-41/coverage_widget.png`

## 6.1 Change & Traceability Links
- change_refs: `CH-003`.
- trace_sections: `TRACEABILITY.md#ws-306-maturity-metrics-snapshots`, `TRACEABILITY.md#fr-41-understanding-coverage-readiness-metrics`.
- artifacts: `docs/REQUIREMENTS_1_3.md`, `docs/CHANGE_REQUEST_003_discovery.md`.

## 7. Acceptance Criteria
- [ ] Coverage metrics report `% of targeted files/modules with structure + intent maps` and percentage of mapped relationships.
- [ ] Readiness heatmap categorizes change zones (e.g., `ready`, `needs tests`, `high risk`) and links back to System Model Graph nodes.
- [ ] `/status` CLI outputs coverage %, freshness timestamp, and discovery mode used for latest manifests.
- [ ] Historical manifest snapshots retained per change (FR-38) and accessible in metrics history.
- [ ] Metrics YAML includes `generated_at`, `inputs`, `trend` section (even if `n/a` on first run).

## 8. Dependencies
- FR-38 discovery pipeline.
- FR-39 System Model Graph.
- FR-40 seeds (metrics should inform seed readiness checklists).
- Observability/CLI infrastructure.

## 9. Risks & Assumptions
- Need to guard against misleading coverage numbers on large repos—allow scoping to focus zones.
- Metrics pipeline must remain fast enough for CLI usage (<3s); consider caching.
- Ensure metrics degrade gracefully when partial discovery runs occur (mark as `partial`).

## 9.1 Retention Notes
- Store metrics snapshots per change in `analysis/metrics/history/`; prune older than 90 days unless flagged `--retain`.

## 10. Review Status
| Field | Value |
| --- | --- |
| **Status** | Draft |
| **Reviewed By** | _Pending_ |
| **Date** | 2025-11-04 |
| **Linked Change** | CH-003 |
