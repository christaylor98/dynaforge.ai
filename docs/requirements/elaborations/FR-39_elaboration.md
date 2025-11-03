---
fr_id: FR-39
ch_refs:
  - CH-003
trace_links:
  - TRACEABILITY.md#fr-39-system-model-graph-yaml-projections
status: Draft
---
# 🧩 Requirement Elaboration — FR-39

## 1. Summary
Establish a System Model Graph represented as versioned YAML projections capturing structure, behavior, intents, requirements, tests, risks, and their relationships so every agent shares a canonical understanding of the system.

## 2. Context & Rationale
- Discovery outputs (FR-38) create manifests but require a cohesive knowledge graph to drive orchestration.
- YAML projections provide transparent, diffable artifacts for audits while allowing agents to hydrate local caches for performant queries.
- Agents (RA, IA, PM, QA) must resolve cross-domain links without relying on stale documents.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| discovery_manifests | YAML/MD paths | `analysis/system_manifest.yaml` | Primary source for node creation. |
| repo_metadata | JSON/YAML | `analysis/repo_metadata.yaml` | Contains commit SHA, branch, timestamps. |
| agent_annotations | JSONL | `artifacts/annotations/discovery.jsonl` | Optional overlay for manual corrections. |
| config | YAML | `config/system_model.yaml` | Controls schema version, retention, optional fields. |

### Edge & Error Inputs
- Invalid schema version → reject with error `SMG_SCHEMA_MISMATCH` and provide upgrade instructions.
- Missing required manifest sections → mark corresponding nodes as `state: incomplete` to avoid blocking pipeline.
- Conflicting node IDs → log `collision` entry in audit and preserve previous version for diffing.

## 4. Process Flow
```mermaid
flowchart TD
  A[Load discovery manifests] --> B[Normalize nodes]
  B --> C[Derive relationships (depends_on, implements, tested_by)]
  C --> D[Validate schema & invariants]
  D --> E[Write YAML projections under analysis/system_model/]
  E --> F[Emit hash + digest for audit]
  F --> G[Hydrate optional local cache (SQLite/Graph DB)]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| YAML | `analysis/system_model/components.yaml` | RA, IA, PM |
| YAML | `analysis/system_model/relationships.yaml` | PM, QA, Implementer |
| YAML | `analysis/system_model/coverage.yaml` | Analytics Lead (FR-41) |
| JSON (optional cache) | `artifacts/system_model/cache.db` | Local agent runtime (not checked-in) |

## 6. Mockups / UI Views
- GraphQL schema sketch: `artifacts/mockups/FR-39/schema.graphql`
- Example node visual: `artifacts/mockups/FR-39/diagram.png`

## 6.1 Change & Traceability Links
- change_refs: `CH-003`.
- trace_sections: `TRACEABILITY.md#ws-09-discovery-foundations`, `TRACEABILITY.md#fr-39-system-model-graph-yaml-projections`.
- artifacts: `docs/CHANGE_REQUEST_003_discovery.md`, `docs/REQUIREMENTS_1_3.md`.

## 7. Acceptance Criteria
- [ ] System Model Graph YAML written under `analysis/system_model/` with separate nodes/edges files and schema version header.
- [ ] Each node includes `id`, `type`, `source_manifest`, `last_updated`, `confidence`.
- [ ] Relationships cover at least `depends_on`, `implements`, `tested_by`, `related_change`, with bidirectional lookup support.
- [ ] Repo history retains previous graph versions for diffing; commit includes hash summary in audit logs.
- [ ] CLI `codexa discover` reports graph refresh status; failure exits with non-zero code and actionable message.

## 8. Dependencies
- FR-38 discovery manifests.
- FR-41 metrics extraction.
- Tooling: YAML validation, hashing utilities, optional SQLite generator.

## 9. Risks & Assumptions
- Graph size could be large; ensure projection chunking (per component) to keep files manageable.
- Schema evolution must preserve backward compatibility or include migration tooling.
- Agents relying on caches must gracefully handle stale data vs. canonical YAML.

## 9.1 Retention Notes
- Retain last 10 projections in Git history; older versions accessible via tags. Local caches may be purged after 7 days unless flagged `--retain`.

## 10. Review Status
| Field | Value |
| --- | --- |
| **Status** | Draft |
| **Reviewed By** | _Pending_ |
| **Date** | 2025-11-04 |
| **Linked Change** | CH-003 |
