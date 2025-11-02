# Retro Follow-ups — CH-001

Tracks items identified during the CH-001 retrospective that require deeper design or multiple changes. Use this list to seed future change requests or backlog tickets.

## Items
- **Automate audit replay generation** — Replace manual heredoc updates for `audit/sample_handoff.jsonl`, `audit/handoff_ms01_phase0.jsonl`, etc., with a scripted flow.
- **Documentation sync tooling** — Provide a reusable command to refresh `PROJECT_OVERVIEW.md`, `PROJECT_DETAIL.md`, `IMPLEMENTATION_PLAN.md`, and `VERSION_CONTROL.md` in one pass when evidence updates.
- **Configurable human oversight levels** — Define a policy/config that lets teams choose minimal/standard/high involvement per change or project.
- **Metrics definition and dashboard** — Decide on key delivery metrics (stage duration, automation ratio, approvals) and implement reporting/dashboards after definition.
- **Extended status board / dashboard** — Once the lightweight board proves useful, scale to a richer view or integration (CLI/HTML).
- **Agent context improvements (advanced)** — Beyond the immediate prompt cleanup, consider structured context packs or knowledge bases for future milestones.

_Source: `docs/RETRO_CH-001.md` (2025-11-02)._
