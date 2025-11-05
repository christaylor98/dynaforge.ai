# .codexa/ Operating Model Root

This directory hosts the project-scoped Codexa configuration. All commands
discover this folder first and fall back to the global control plane
(`~/.config/codexa/`) only when necessary.

## Layout
- `config.yaml` — project entry point, may list `extends:` references to shared bundles.
- `agents/` — agent-specific configuration overrides, prompts, or manifests.
- `rules/` — lint, policy, or governance rules that are project-specific.
- `workflows/` — orchestrations and scripts for Codexa CLI invocations.
- `manifests/` — discovery outputs (`system_manifest.yaml`, `change_zones.md`, `intent_map.md`, etc.).
- `logs/` — optional runtime logs emitted by agents/commands (ignored by default).
- `state/` — optional cached state; treated as ephemeral.

## Provenance Logging
`codexa doctor config` computes and records:
- Resolved `config_root`
- `extends_from` chain
- Template hash of the global bundle
- Manifest hash for the latest discovery run

These values appear in audit logs (`audit/*.jsonl`) and status documentation per CR004 / FR-06.

## Migration Notes
Legacy Spec-Kit repositories should run `codexa migrate spec-kit` to populate this
folder. The command performs a dry run by default and documents required
manual follow-ups.
