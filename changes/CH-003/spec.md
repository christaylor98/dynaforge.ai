# CH-003 Specification — MS-03 Operating Model Integration

## Scope
- Implement `.codexa/` scaffolding enforcement (FR-42).
- Publish and version the global control-plane bundle with provenance hashing (FR-43).
- Add configuration validation tooling and telemetry (`codexa doctor config`) (FR-44).
- Update existing requirements to respect configuration lineage: FR-01, FR-02, FR-06, FR-32, FR-38, FR-39.

## Deliverables
| Artifact | Description |
| --- | --- |
| `.codexa/` lint + migration tooling | CLI commands, docs, CI guardrails. |
| Global control-plane bundle | Versioned templates in `~/.config/codexa/` with change log. |
| `codexa doctor config` | CLI command with JSON output, tests, telemetry integration. |
| Audit/status schema updates | New `config_root`, `extends_from`, `template_hash` fields. |
| Discovery + maturity updates | Manifests stored under `.codexa/manifests/`, metadata relocation. |
| Evidence bundle | TC-FR42-001, TC-FR43-001, TC-FR44-001, TC-FR06-002, TC-FR32-001, TC-FR38-001, TC-FR39-001. |

## Out of Scope
- Remote configuration registry or hosted control-plane distribution.
- Advanced policy automation leveraging new provenance data (defer to future governance CR).

## Risks & Mitigations
| Risk | Mitigation |
| --- | --- |
| Legacy projects missing `.codexa/` | Provide migration helper with rollback, allow temporary warning mode. |
| Bundle sync drift | Include hash verification + change log, surface warnings in doctor output. |
| CI failures due to environment variance | Support explicit `--config-root` and degrade gracefully with warnings. |

## Acceptance
- All targeted requirements marked at least `IN PROGRESS` with tests added/passing.
- Milestone MS-03 readiness checklist completed (lint, doctor, audit sample, metadata migration).
