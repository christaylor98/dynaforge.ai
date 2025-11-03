# CHANGE REQUEST 003 — Discovery-Centric System Model

## Summary
Codexa must treat deep understanding of existing systems as the primary artifact. This change request formalizes a discovery-first capability that captures reality, intent, and change readiness before execution. The outcome is a living model (`system_model.db` + YAML projections) and a supporting workflow that turns undocumented codebases into actionable change journeys.

## Drivers
- Teams routinely inherit codebases with sparse documentation, stale tests, and unclear ownership.
- Requirement-first approaches struggle to bootstrap truth from these codebases, causing costly discovery spikes.
- Codexa’s value proposition hinges on turning any system—monolith, script, or blank slate—into a navigable, evolvable environment.

## Objectives
- Position Codexa as an understanding engine where change begins with shared comprehension.
- Deliver lightweight, repeatable discovery artifacts (`system_manifest.yaml`, `change_zones.md`, `intent_map.md`) that guide plan formation.
- Support both “code-only” and “well-documented” repos through a consistent CLI/agent experience.
- Feed all discovery outputs into a persistent System Model Graph that aligns requirements, tests, and change plans.

## Scope
In scope:
- Discovery agents, CLI entry points, manifest schemas, and storage contracts.
- System Model Graph design and integration into the existing forge workflow.
- Understanding-Centric Engineering manifesto and tagline adoption (“Software re-imagined — from understanding to evolution.”)

Out of scope (deferred to later phases):
- Advanced visualization dashboards.
- Full runtime observability/probing integrations.

## Proposed Architecture

### Layered Operating Model

| Layer | Purpose | Key Outputs | Primary Agent(s) |
| --- | --- | --- | --- |
| Discovery & Scope Framing | Rapid structural awareness without full comprehension | `system_manifest.yaml` | `analyzer`, `doc_analyzer`, `interface_mapper`, `intent_mapper` |
| Change Seed | Choose where to begin transformation | Ranked change zones, `CHANGE.yaml`, baseline tests | `seed_planner`, `test_bootstrapper` |
| Progressive Understanding | Deepen knowledge as change touches new areas | Dependency expansions, behavior traces, storyboard reviews | `context_enricher`, `storyboarder` |
| Integration | Wire artifacts into forge loop | Traceable plan/test hooks | `forge_manager` |

### Code-Only Mode (Fallback)
When documentation is absent, Codexa still produces:
- **Structure Map** (`analysis/structure_map.yaml`): language inventory, dependency graph, symbol map, complexity metrics.
- **Behavior Map** (`analysis/behavior_map.yaml`): entry points, IO interactions, data flow sketches.
- **Intent Map** (`analysis/intent_map.md`): inferred capability clusters and use cases.
- **Change Readiness Heatmap**: complexity, coupling, doc density, AI confidence.

CLI support:
```
codexa discover --mode=code-only
codexa summarize --focus "<topic>"
codexa suggest-change-zones
```

## System Model Graph
- Acts as the shared memory for Codexa (functions, modules, behaviors, intents, requirements, tests, risks, metrics).
- Stores edges such as `depends_on`, `implements`, `tested_by`, `derived_from`, `contradicts`, `superseded_by`.
- Backed by `system_model.db` with GraphQL/REST adapters and YAML projections for portability.
- Every discovery confirmation, change seed, and test result updates the graph, ensuring projections (requirements, architecture notes, storyboards) remain in sync.

## Ethos Alignment
Change Request 003 operationalizes Understanding-Centric Engineering:
1. **Start from what exists:** treat legacy code as frozen intelligence to be reinterpreted.
2. **Understanding is truth:** documents and tests become projections of the living model.
3. **Change emerges from comprehension:** clarity precedes action.
4. **Evolution replaces maintenance:** each modification reinforces the shared model.
5. **Progress measured by clarity:** track understanding coverage alongside velocity.
6. **We forge, not rebuild:** respect and strengthen working systems.
7. **Tools learn with humans:** every clarification enriches the model.

## Roadmap
| Phase | Focus | Deliverables |
| --- | --- | --- |
| 1 | Code-only discovery & intent mapping MVP | `system_manifest.yaml`, `intent_map.md` generated on sample repo |
| 2 | System Model Graph implementation | `system_model.db` schema, API access layer |
| 3 | Projected views | Auto-generated `Requirements.md`, `Architecture.md`, storyboard exports |
| 4 | Change tracking integration | Before/after deltas embedded in graph |
| 5 | Continuous understanding loop | Model updates on every code or goal change (+ telemetry) |

## Near-Term Deliverables
- Discovery CLI prototype with `discover`, `summarize`, and `suggest-change-zones`.
- Manifest schemas and representative outputs under `analysis/`.
- Change Seed template (manifest, baseline tests, context extraction).
- `UNDERSTAND_AND_EVOLVE.md` manifesto and README hero update with new tagline.
- Understanding coverage metrics surfaced via CLI status.

## Immediate Next Actions
1. Confirm manifest schema drafts and persistence approach for the System Model Graph.
2. Build discovery MVP to produce structure, behavior, and intent maps for a target repo.
3. Draft manifesto and update README hero section.
4. Instrument CLI to report understanding coverage and change readiness metrics.
5. Plan code-only usability test on a large, undocumented codebase to validate flow.
