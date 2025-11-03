---
fr_id: FR-24
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#ws-207-interaction-cli-extensions
  - TRACEABILITY.md#fr-24-impact-and-trace-commands
status: Draft
---

# 🧩 Requirement Elaboration — FR-24

## 1. Summary
Extend the interaction CLI/Discord bridge with `/impact`, `/trace`, `/change`, and `/approve` commands that operate consistently across local and remote contexts, exposing change-centric insights on demand.

## 2. Context & Rationale
Stakeholders need quick access to change scope, traceability status, and approval progress—without digging into files. FR-24 builds on FR-08/09 by providing richer informational commands, aligning human visibility with the governance flow described in CR002.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `command_payload` | JSON (`pipelines/interaction_stub.py`) | `{"cmd":"/trace","args":["FR-24"],"channel":"discord"}` | Normalized event. |
| `impact_report` | Markdown (`docs/IMPACT_REPORT.md`) | `## CH-017` | Source for `/impact`. |
| `traceability_matrix` | Markdown (`TRACEABILITY.md`) | FR/WS mapping | Source for `/trace`. |
| `change_registry` | Markdown (`CHANGELOG.md`) | `CH-017` entry | Used by `/change`. |
| `approval_status` | JSON (`artifacts/phase1/approvals/events.jsonl`) | Latest approvals | Drives `/approve` responses. |

### Edge & Error Inputs
- Unknown FR/CH ID → respond with helpful error and link to `/change.list`.
- Large traceability output → paginate response or attach summary file to avoid flooding chat.
- Remote command fails (Discord webhook) → queue retry and inform user of delay.

## 4. Process Flow
```mermaid
flowchart TD
  A[Receive command] --> B[Validate permissions + context]
  B --> C[Fetch data from relevant artifact]
  C --> D[Render response (table, bullet, summary)]
  D --> E[Send reply (CLI/Discord) + log audit entry]
  E --> F[Optional: cache response for quick replays]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| Text / Markdown | Response message with tables | Human stakeholders |
| JSONL | `audit/commands.jsonl` enriched entries | Governance |
| Cache | `artifacts/interaction/cache.json` | Performance optimization |

## 6. Mockups / UI Views (if applicable)
- `artifacts/mockups/FR-24/impact_command.md` — CLI output.
- `artifacts/mockups/FR-24/trace_command_discord.md` — Discord embed.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, plus the `CH-###` referenced during commands.
- `trace_sections`: `TRACEABILITY.md#ws-207-interaction-cli-extensions`, `TRACEABILITY.md#fr-24-impact-and-trace-commands`.
- `artifacts`: `audit/commands.jsonl`, `CHANGELOG.md`, `docs/IMPACT_REPORT.md`.

## 7. Acceptance Criteria
* [ ] `/impact CH-###` returns summary of risk, affected FR/WS/TC, and open concerns from latest IA report.
* [ ] `/trace FR-XX` returns linked changes, workstreams, tests, and open QA gaps.
* [ ] `/change CH-###` displays lifecycle state, staged approvals, retention status, and recent concerns.
* [ ] `/approve CH-###` reuses FR-10 gate logic, returning next required stage if caller lacks authority.

## 8. Dependencies
- FR-08/09 command infrastructure.
- FR-16/17/21/27 outputs for data sources.
- FR-28 `/df.*` commands (shared rendering utilities).
- WS-207 Interaction CLI Extensions.

## 9. Risks & Assumptions
- Data volume may exceed chat limits; implement summarization and optional attachments.
- Permissions must be enforced using RACI matrix; unauthorized use should be gracefully rejected.
- Keep responses idempotent and cache results to avoid repeated heavy reads.

## 9.1 Retention Notes
- When responses reference retained runs, include note (e.g., “Implementer run retained for GO review”) so humans know evidence availability timelines.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
