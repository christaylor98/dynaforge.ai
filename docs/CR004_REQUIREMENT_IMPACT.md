# CR004 Requirement Impact & Clarifications

## Context
- Change request `docs/CHANGE_REQUEST_004_operating_model.md` codifies the Codexa operating model: `.codexa/` as the canonical project root, optional inheritance from `~/.config/codexa/`, and CLI discovery precedence.
- The repo must expose predictable configuration artifacts so agents, CLI commands, and governance tooling behave identically across local runs, CI, and hosted environments.
- Compatibility with Spec-Kit requires migration guidance and scaffolding that respects legacy layouts while enforcing the new hybrid discovery model.
- Scope is captured as milestone **MS-03 Operating Model Integration** in `TRACEABILITY.md`, focusing delivery on FR-42–FR-44 plus supporting updates to FR-01/FR-02/FR-06/FR-32/FR-38/FR-39.

## Updated Requirements
| Requirement ID | Current Focus | Required Update from CR004 | Effort (est.) | CR004 Source |
| --- | --- | --- | --- | --- |
| FR-01 Project Manager | Orchestrates maturity-aware agent loop with discovery pre-flight. | Load operating context from resolved `.codexa/config.yaml`; persist discovery mode plus `config_root` (project vs global) in run metadata before dispatching agents. | Medium | Operating Model → Hybrid Root Discovery; Implementation Considerations. |
| FR-02 Status Documentation | Keeps overview/detail docs aligned with active change state. | Reference `.codexa/README.md`, document config inheritance lineage, and surface the resolved config root + template versions in hero sections. | Low-Medium | Project Layout; Global Control Plane. |
| FR-06 Structured Handoffs & Audit Trails | Captures agent handoffs with rich metadata. | Append `config_root`, `extends_from`, and `.codexa` artifact hashes to audit entries so replay can reconstruct configuration lineage. | Medium | Operating Model → Hybrid Root Discovery; Implementation Considerations. |
| FR-32 Project Metadata Source | Maintains maturity data for agents. | Relocate canonical metadata under `.codexa/` (e.g., `.codexa/project_metadata.yaml`), support `extends:` pointers to global defaults, and log provenance in maturity updates. | Medium | Project Layout; Global Control Plane. |
| FR-38 Discovery Pipeline Artifacts | Generate manifests/metrics across modes. | Respect `.codexa/manifests/` layout, honour global template includes, and emit warnings if scaffolding is missing. | Medium | Project Layout; Implementation Considerations. |
| FR-39 System Model Graph Projections | Persist understanding graph outputs. | Store projections under `.codexa/manifests/` with `extends` metadata, ensuring graph refresh honours resolved configuration precedence. | Medium | Success Metrics; Implementation Considerations. |

## New Requirements
| Proposed ID | Requirement Summary | Primary Owner | Effort (est.) | Motivation from CR004 |
| --- | --- | --- | --- | --- |
| FR-42 | Scaffold and validate the `.codexa/` project root with required subdirectories (`config.yaml`, `agents/`, `rules/`, `workflows/`, `manifests/`, `README.md`) and lint for schema compliance. | Platform Tooling / PM Agent | Medium | Project Layout (`.codexa/`); Deliverables. |
| FR-43 | Provide a global control-plane bundle (`~/.config/codexa/`) with versioned defaults, template registry, and governance policies consumable via `extends:`. | Platform Architecture | Medium | Global Control Plane; Success Metrics. |
| FR-44 | Implement CLI configuration discovery and validation (`codexa doctor config`) covering project-only, global-only, and hybrid scenarios, with automated tests. | CLI / Dev Experience | Medium | Hybrid Root Discovery; Implementation Considerations. |

## Effort Notes
- Configuration lineage must be exposed consistently across CLI telemetry, audit logs, and status docs—expect cross-cutting updates touching PM agent utilities, logging middleware, and documentation templates.
- New scaffolding and validation commands share infrastructure with existing discovery CLI work; reuse manifest/schema validators to reduce duplication.
- Migration support for Spec-Kit projects should bundle with FR-42 deliverables (templates + conversion script).

## Suggested Refinements
- Publish a short compatibility matrix (Spec-Kit vs Codexa) within `.codexa/README.md` to ease migration reviews.
- Add CI guardrails that block merges if required `.codexa/` files are missing or misconfigured.
- Capture config provenance hashes in traceability evidence to simplify audits and rollback analysis.

## Clarification Responses
1. **Global vs project precedence** — Project `.codexa/` overrides global defaults; multiple `extends:` entries resolve depth-first while detecting cycles.
2. **Location of legacy metadata files** — Existing metadata/docs remain readable, but authoritative copies must move under `.codexa/`; backward links stay as mirrors until migration completes.
3. **Spec-Kit projects without `.codexa/`** — Provide a migration script (`codexa migrate spec-kit`) that scaffolds `.codexa/` and maps legacy paths; treat migration as part of FR-42 acceptance.
Lets leave this for a latter discussion, I'm not really sure this is a great path forward yet.  The only value I see is a bit of a lift in requirement understanding for initial discovery run.
