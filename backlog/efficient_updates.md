# Efficient Discovery/Analysis Updates — Follow-up issue-12

## Goal
Eliminate redundant AI effort when reconciling discovery and analysis by scoping recomputation to the true impact area of a change.

## Agreed Strategy
- **Hash-Based Drift Detection**  
  - Persist SHA-256 hashes for key discovery artifacts (`analysis/system_manifest.yaml`, `analysis/change_zones.md`, `analysis/intent_map.md`, future graph exports).  
  - Before triggering agents, compare hashes against the previous run and treat unchanged artifacts as stable.

- **Blast-Radius Expansion**  
  - Seed the blast radius with hash-mismatched components.  
  - Expand via dependency graph edges (code ↔ docs ↔ tests).  
  - Inject failing regression tests and policy violations into the radius automatically.

- **Adaptive Agent Activation**  
  - Change Impact Analyzer determines which agents re-run, based on radius size + risk (local, subsystem, architectural).  
  - Lightweight status snapshot for “local” radius; full orchestration only when the radius escalates.

- **Feedback Loop & Metrics**  
  - Track misses where failures occur outside the computed radius; feed results into analyzer heuristics.  
  - Metrics: `% components skipped`, AI runtime saved vs baseline, blast expansion rate, false-negative count.

- **Human Oversight**  
  - PM can override or approve the auto-calculated radius for high-impact work before orchestration proceeds.

## Implementation Notes
- `codexa discover` (backed by `scripts/discovery_bootstrap.py`) now emits artifact hashes, powering hash-diff detection.  
- Phase 1 tasks: persist previous hashes, build the radius planner, expose coverage/skip metrics via `/status`.

_Outcome: issue-12 follow-up resolved; blast-radius efficiency improvements documented and instrumented._
