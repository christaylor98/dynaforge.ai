# CHANGE REQUEST 004 — Codexa Operating Model

## Summary
Codexa must present a clear operating model that honors its Spec-Kit lineage while supporting centralized governance. This change request formalizes a hybrid configuration strategy that treats `.codexa/` as the canonical project root, with optional inheritance from a global control plane. The outcome is a consistent discovery process, predictable file layout, and explicit rules for how Codexa locates the intelligence it needs to run in any repository. This scope anchors milestone **MS-03 Operating Model Integration** (see `TRACEABILITY.md`).

## Drivers
- Stakeholders expect Codexa to feel like an evolution of Spec-Kit, where automation and knowledge travel with the codebase.
- Teams need shared defaults and reusable agents without copy-pasting templates into every repo.
- Lack of a documented discovery order risks drift between local setups, CI environments, and hosted agents.
- The operating model must scale from solo usage to multi-repo, multi-team deployments without rework.

## Objectives
- Define Codexa’s configuration hierarchy and discovery logic.
- Standardize the `.codexa/` project folder layout and required artifacts.
- Support inheritance from a global config (`~/.config/codexa/`) to reduce duplication.
- Provide migration guidance for existing Spec-Kit projects and Codexa experiments.
- Document the operating model so it can plug into traceability, RACI, and change management artifacts.

## Scope
**In scope**
- Operating model narrative and diagrams when needed.
- CLI and agent behavior for configuration discovery and precedence.
- Folder conventions, required files, and optional extensions under `.codexa/`.
- Global control-plane layout (`~/.config/codexa/`) and include/extend semantics.
- Change management hooks (e.g., how change requests consume the operating model).

**Out of scope**
- Network-based configuration registries or remote templates.
- UI dashboards or visualization tooling for configuration introspection.
- Advanced policy enforcement (leave to future governance change request).

## Operating Model

### Hybrid Root Discovery
- Codexa searches upward from the current working directory until it finds `.codexa/`.
- If no project folder exists, Codexa falls back to `~/.config/codexa/`.
- Precedence: project overrides > project includes > global defaults > built-ins.
- CLI supports explicit `--config-root` (mainly for tooling/tests) but defaults to auto-discovery.

### Project Layout (`.codexa/`)
- `config.yaml`: primary entry point; may declare `extends:` to reference global templates.
- `agents/`, `rules/`, `workflows/`: opinionated directories for agent manifests, rule sets, and orchestrations.
- `manifests/`: generated or curated outputs (`system_manifest.yaml`, `intent_map.md`).
- `logs/` and `state/`: optional runtime outputs managed by agents (subject to retention policy).
- `README.md`: human-friendly explainer of project-specific Codexa assets.

### Global Control Plane (`~/.config/codexa/`)
- `core.yaml`: ships shared defaults, agent templates, and governance guardrails.
- `templates/`: reusable snippets (`discovery.yaml`, `ms02_storyboard.yaml`).
- `policies/`: shared QA, security, and RACI policies referenced by projects.
- Supports semantic versioning and change logs to coordinate updates across teams.

### Compatibility with Spec-Kit
- Provide a `spec-kit` import path that maps historical folders into the new layout.
- Supply migration scripts/examples so existing Spec-Kit repositories can adopt Codexa with minimal churn.
- Document behavioral differences (e.g., new precedence rules, manifest naming) and test expectations.

## Implementation Considerations
- Update CLI bootstrap commands (`codexa init`, `codexa discover`, etc.) to scaffold and validate the structure.
- Add configuration resolution tests covering local-only, global-only, and hybrid scenarios.
- Ship reference manifests under `analysis/` to demonstrate expected outputs.
- Align traceability artifacts (`TRACEABILITY.md`) to reference the new operating model.
- Ensure agents respect read/write permissions when working inside `.codexa/`.

## Deliverables
- `docs/CHANGE_REQUEST_004_operating_model.md` (this document) and a companion operating model guide.
- Updated CLI/agent documentation describing discovery logic and folder expectations.
- Migration checklist for Spec-Kit projects.
- Scripts or templates that scaffold `.codexa/` with extend hooks into global configs.
- Test coverage (unit + integration) for configuration resolution and fallbacks.

## Success Metrics
- 100% of Codexa-managed repositories host a `.codexa/` folder aligned with this spec.
- Global control-plane updates roll out without manual project edits (inheritance proves effective).
- CI and local runs resolve identical configs in smoke tests.
- Positive feedback from at least one Spec-Kit migration trial.

## Immediate Next Actions
1. Draft the detailed operating model guide (diagrams, examples, FAQs).
2. Update CLI discovery code and tests to implement precedence logic.
3. Scaffold reference `.codexa/` and global control-plane templates.
4. Run a migration exercise on an existing Spec-Kit project and capture notes.
5. Sync TRACEABILITY and RACI docs to reference the new operating model artifacts.
