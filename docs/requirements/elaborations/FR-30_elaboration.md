---
fr_id: FR-30
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#ws-306-maturity-metrics--snapshots
  - TRACEABILITY.md#fr-30-change-velocity-dashboard
status: Draft
---

# 🧩 Requirement Elaboration — FR-30

## 1. Summary
Implement a change velocity dashboard that reports weekly and milestone metrics—through CLI and dashboards—covering throughput, cycle time, approval latency, and risk posture.

## 2. Context & Rationale
Stakeholders need quantitative insight into Dynaforge’s delivery cadence. By aggregating metrics from change workspaces, approvals, and QA verdicts, FR-30 enables data-driven planning and governance oversight. It complements PM status updates (FR-02) and maturity tracking (FR-36).

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `change_history` | Markdown (`CHANGELOG.md`) | Entries with timestamps | Source data. |
| `approval_events` | JSONL (`artifacts/phase1/approvals/events.jsonl`) | Stage decisions | For latency metrics. |
| `implementer_runs` | JSON (`artifacts/work/retention_index.json`) | Start/end times | Cycle time measurement. |
| `qa_verdicts` | JSON (`artifacts/phase3/qa/verdicts/*.json`) | PASS/BLOCK | QA gating stats. |
| `config` | YAML (`configs/velocity_dashboard.yaml`) | metric definitions | Allows custom thresholds. |

### Edge & Error Inputs
- Missing timestamps → dashboard shows `unknown`, logs data-quality warning, and requests fix.
- Inconsistent timezones → normalize to UTC before calculations.
- Data volume high → downsample older periods to keep CLI fast.

## 4. Process Flow
```mermaid
flowchart TD
  A[Ingest change & approval history] --> B[Compute metrics (cycle time, throughput, latency)]
  B --> C[Calculate trend lines and risk posture]
  C --> D[Render CLI table + generate dashboard artifacts]
  D --> E[Publish summary to docs/metrics and change workspace]
  E --> F[Notify PM/GO with highlights]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| JSON | `artifacts/metrics/velocity_weekly.json` | PM, Governance |
| Markdown | `docs/metrics/CHANGE_VELOCITY.md` | Stakeholders |
| CLI | `/status velocity` report | Humans via CLI/Discord |
| Charts | `artifacts/metrics/velocity_trend.png` (optional) | Presentations |

## 6. Mockups / UI Views (if applicable)
- `artifacts/metrics/screenshots/velocity_cli.md` — CLI output.
- `artifacts/metrics/screenshots/velocity_chart.md` — Graphical trend.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, plus aggregated `CH-###` history.
- `trace_sections`: `TRACEABILITY.md#ws-306-maturity-metrics--snapshots`, `TRACEABILITY.md#fr-30-change-velocity-dashboard`.
- `artifacts`: `CHANGELOG.md`, `docs/metrics/CHANGE_VELOCITY.md`, `artifacts/metrics/velocity_weekly.json`.

## 7. Acceptance Criteria
* [ ] Dashboard exposes at least cycle time, throughput (changes/week), approval latency, QA block rate, and retention counts.
* [ ] `/status velocity` summarises current milestone progress vs target.
* [ ] Metrics integrate with maturity snapshots (FR-36) and PM status docs (FR-02) within one orchestration cycle.
* [ ] Historical data preserved (rolling 12 weeks) for trend analysis.

## 8. Dependencies
- FR-25 change workspaces, FR-10 approval logs, FR-11 QA verdicts.
- FR-36 maturity metrics for integrated reporting.
- WS-306 Maturity Metrics & Snapshots.

## 9. Risks & Assumptions
- Metric accuracy depends on consistent timestamps and event logging; enforce in automation.
- Visualization may require third-party libs; ensure offline rendering fallback (ASCII tables).
- Rapid growth in change volume may require data warehouse; plan for future scaling.

## 9.1 Retention Notes
- Dashboard should note when metrics include retained runs awaiting purge to contextualize cycle time spikes.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
