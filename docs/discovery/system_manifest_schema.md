# System Manifest Schema — MS-02 Phase 0 Baseline

The discovery manifest is the canonical snapshot of repository understanding. This Phase 0 schema establishes the contract that the automated discovery pipeline (FR-38/FR-39/FR-41) must honor.

## 1. File Location
- Path: `analysis/system_manifest.yaml`
- Owner: Discovery Analyzer (accountable: Project Manager)
- Related artifacts: `analysis/change_zones.md`, `analysis/intent_map.md`, `docs/discovery/config.yaml`
- Generator: `codexa discover` (backed by `scripts/discovery_bootstrap.py`)

## 2. Top-Level Structure
```yaml
metadata:        # Run metadata, ownership, audit anchors
inputs:          # Source configuration and context references
summary:         # Phase/status snapshot, metrics, artifact links
architecture:    # Layer descriptions tied to components
components: []   # Detailed component entries with traceability
artifacts:       # Related evidence paths (audit, governance, change)
dependencies_external: # Tooling and external dependencies
risks_and_gaps:  # Outstanding issues or assumptions
next_actions: [] # Recommended follow-up steps
```

### 2.1 `metadata`
| Field | Type | Notes |
| --- | --- | --- |
| `version` | semver | Manifest schema version. |
| `generated_at` | ISO 8601 | UTC timestamp of the snapshot. |
| `repo` | string | Repository slug/name. |
| `commit_sha` | string | Git commit hashed by the run. |
| `generator` | string | Tool or mode generating the manifest (`discovery-cli`, `manual-bootstrap`, etc.). |
| `discovery_mode` | enum | `full`, `quick`, `code-only`, or `bootstrap-manual`. |
| `status` | enum | `draft`, `stale`, `current`, `partial`. |
| `owners` | map | RACI-style owner lists (`accountable`, `responsible`, `consulted`, `informed`). |

### 2.2 `inputs`
Captures the configuration and context used:
- `config_file`: path, existence flag, TODO guidance.
- `loop_scope`: scope metadata from `loop-plan.json`.
- `reference_docs`: ordered list for reproducibility.
- `followups_open`: outstanding follow-up IDs.

### 2.3 `summary`
Provides readiness snapshot:
- `project_phase`, `readiness` booleans, `notes`.
- `understanding_metrics`: coverage %, freshness timestamp/source.
- `discovery_artifacts`: current manifest-related files.
- `discovery_artifacts.artifact_hashes`: hashes for supporting artifacts (excluding the manifest itself).
- `language_inventory`: detected languages with root paths.
- `toolchain`: language runtime versions and planned analysis tools.
- `analysis.repository_insights`: per-file structural summary (language, functions, classes, complexity).

### 2.4 `architecture`
Layer summary (`name`, `responsibilities`, `components`). Serves as the bridge into `components`.

### 2.5 `components[]`
Each entry must include:
- `id`, `name`, `paths`.
- `responsibilities`, `dependencies`, and `maturity`.
- `requirements`: list of FR IDs satisfied or targeted.
- `trace_links`: anchors into `TRACEABILITY.md` or other governance docs.

### 2.6 `artifacts`
Groups supporting evidence:
- `audit_trail`: command and handoff logs.
- `discovery_snapshots`: `summary.md`, `gaps.md`, `iteration_log.md`, plus manifest pointers.
- `milestone_assets`: storyboard and loop planning references.
- `change_work`: links to relevant change objects.

### 2.7 `dependencies_external`
Lists external tooling (Python modules, CLI tools, analysis stacks).

### 2.8 `risks_and_gaps`
Structured gap list for governance review (`id`, `description`, `mitigation`, `status`).

### 2.9 `next_actions`
Ordered list of recommendations feeding the follow-up workflow.

## 3. Compliance Expectations
- **Traceability**: Every `requirements` entry in `components` must map to an active row in `TRACEABILITY.md`.
- **Auditability**: `metadata.commit_sha` and `summary.discovery_artifacts` provide reproducibility for each manifest.
- **Automation**: Once the discovery CLI is implemented, all `todo` notes must be programmatically managed (warnings logged when placeholders remain).
- **Retention**: Manifests should remain under version control; large derived assets belong in `artifacts/discovery/` with timestamped subdirectories.

## 4. Open Items for Phase 1
- Replace manual owners with agent identifiers pulled from the RACI matrix.
- Add hash digests for each referenced artifact.
- Introduce `system_model` pointer once the graph builder lands.
- Emit JSON schema or OpenAPI definition to support validation tooling.
