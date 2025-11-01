---
fr_id: FR-36
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#ws-306-maturity-metrics--snapshots
  - TRACEABILITY.md#fr-36-maturity-metrics-tracking
status: Draft
---

# 🧩 Requirement Elaboration — FR-36

## 1. Summary
Track maturity metrics—time-in-level, upgrade count, active criteria—and surface them in `PROJECT_OVERVIEW.md` and CLI `/status`, providing transparency into governance progress.

## 2. Context & Rationale
Alongside change velocity (FR-30), stakeholders need to know how the project moves through maturity levels. FR-36 aggregates metadata, review outcomes, and criteria completion to produce dashboards and status snippets that inform planning and compliance.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `project_metadata` | YAML (`PROJECT_METADATA.md`) | `last_review: 2025-10-30` | Source data. |
| `maturity_reviews` | JSON (`artifacts/metrics/maturity_reviews.json`) | review history | For counts. |
| `criteria_status` | YAML (`configs/maturity_criteria.yaml`) | satisfies criteria | Evaluated per level. |
| `change_history` | Markdown (`CHANGELOG.md`) | maturity change entries | Tracks transitions. |
| `status_docs` | Markdown (`docs/PROJECT_OVERVIEW.md`) | Output target | Updated with metrics. |

### Edge & Error Inputs
- Missing review history → metrics mark value as `unknown`, notify Governance Officer.
- Criteria config changed without review → highlight pending revalidation.
- CLI rendering exceeds width → provide condensed view with optional `--details`.

## 4. Process Flow
```mermaid
flowchart TD
  A[Collect metadata + review history] --> B[Compute metrics (time-in-level, upgrades, criteria completion)]
  B --> C[Update overview docs + CLI cache]
  C --> D[Publish metrics JSON for dashboards]
  D --> E[Notify stakeholders via /status maturity]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| JSON | `artifacts/metrics/maturity_overview.json` | Dashboards |
| Markdown | `docs/PROJECT_OVERVIEW.md` maturity section | Stakeholders |
| CLI | `/status maturity` output | Humans |
| JSONL | `audit/maturity_metrics.jsonl` | Audit |

## 6. Mockups / UI Views (if applicable)
- `artifacts/metrics/screenshots/maturity_cli.md`
- `artifacts/metrics/screenshots/maturity_overview_card.md`

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, plus relevant maturity changes.
- `trace_sections`: `TRACEABILITY.md#ws-306-maturity-metrics--snapshots`, `TRACEABILITY.md#fr-36-maturity-metrics-tracking`.
- `artifacts`: `PROJECT_METADATA.md`, `docs/PROJECT_OVERVIEW.md`, `artifacts/metrics/maturity_overview.json`.

## 7. Acceptance Criteria
* [ ] Metrics include `current_level`, `days_in_level`, `upgrades_this_year`, `criteria_met`, `criteria_pending`.
* [ ] `/status maturity` and status docs refresh automatically after each maturity review or metadata update.
* [ ] Metrics integrate with change velocity (FR-30) to provide combined view when requested.
* [ ] Fail-safe: if data incomplete, command returns actionable warning and logs concern.

## 8. Dependencies
- FR-32 metadata, FR-33 guide, FR-34 reviews, FR-30 velocity.
- WS-306 Maturity Metrics & Snapshots.

## 9. Risks & Assumptions
- Time-in-level calculations assume accurate review timestamps; ensure timezone handling.
- Without automation, metrics may drift; schedule daily refresh tied to change router.
- Provide guardrails for manual overrides to avoid misleading data.

## 9.1 Retention Notes
- Metrics reference retained runs only indirectly; no additional retention needs beyond recording review artifacts.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
