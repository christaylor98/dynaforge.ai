# Project Overview

## Mission
Build the Codexa.ai framework with auditable agent workflows and human governance checkpoints.

## Current Phase Snapshot
- Phase: `MS-02 — Discovery MVP`
- Status: Discovery-first workflow in progress (context intake → discovery → loop planning → governance summary).
- Primary Contacts: Project Manager Agent, Human PM

## Highlights
- `docs/discovery/config.yaml` now committed as the contract for MS-02 discovery runs; iteration history lands in `docs/status/iteration_log.md`.
- `codexa discover` consumes the config, auto-generates `analysis/system_manifest.yaml`, `analysis/change_zones.md`, `analysis/intent_map.md`, `analysis/metrics/understanding_coverage.yaml`, computes repository insights (functions/classes/complexity), and records blast-radius history for follow-up planning.
- Loop planning prompt captures execution scope in `loop-plan.json`, feeding `codexa seed --from loop-plan` to create scoped bundles.
- Conversational review gates synthesise human feedback into `changes/CH-###/seed/REVIEW.md`, blocking progress until design/test approvals (or waivers) are recorded.
- Governance summaries (`artifacts/ms02/storyboard/summary.md` + `gaps.md`) publish after approval to reflect change readiness and outstanding actions.
- Discovery artifacts (`analysis/system_manifest.yaml`, `analysis/change_zones.md`, `analysis/intent_map.md`) provide the baseline understanding snapshot until automation is live.

## Next Steps
- Finish wiring conversational follow-up handling (FR-38/FR-39 iteration loop) and seed packaging (FR-40) to ready MS-02 demo collateral.
- Populate traceability evidence for updated workstreams (WS-09, WS-110, WS-201, WS-202, WS-306) as they produce artifacts.
- Prepare MS-02 walkthrough using `design/MS-02_storyboard.md` so humans can rehearse the discovery-to-execution flow end-to-end.
- Use `python3 scripts/ms02_dry_run.py` to refresh sample artifacts for demos or onboarding sessions.

## Approvals
- `⏳ Pending — MS-02 discovery loop readiness`

_Updated for MS-02 discovery milestone alignment at 2025-11-04 15:30:00Z._
