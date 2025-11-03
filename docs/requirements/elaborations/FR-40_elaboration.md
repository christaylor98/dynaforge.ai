---
fr_id: FR-40
ch_refs:
  - CH-003
trace_links:
  - TRACEABILITY.md#fr-40-change-seeds-with-manifeststests
status: Draft
---
# 🧩 Requirement Elaboration — FR-40

## 1. Summary
Provide a `codexa seed <zone> <mission>` workflow that packages focused code context, discovery manifests, and baseline tests into a change seed directory, creating the canonical starting point for each change journey.

## 2. Context & Rationale
- After discovery (FR-38/FR-39) we need an actionable slice for implementers and reviewers.
- Change seeds ensure every `CH-###` includes consistent artifacts (manifest, plan skeleton, tests) without manually curating files.
- Supports milestone MS-02 by letting humans and agents jump into the scoped change with traceability intact.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| zone | string | `dashboard` | Must match entry from `analysis/change_zones.md`. |
| mission | string slug | `async-refactor` | Snake/pascal case describing objective. |
| repo_path | path | `.` | Root repo path. |
| options | CLI flags | `--languages python --tests pytest` | Customize scaffolds and language coverage. |

### Edge & Error Inputs
- Unknown zone → CLI error `SEED_ZONE_NOT_FOUND` with list of valid zones.
- Seed already exists → prompt to reuse (`--force` flag) or create new timestamped seed.
- Missing discovery manifests → instruct user to run `codexa discover` first and exit non-zero.

## 4. Process Flow
```mermaid
flowchart TD
  A[Invoke codexa seed] --> B[Load discovery manifests]
  B --> C[Resolve files + dependencies for zone]
  C --> D[Copy/Persist context slice into changes/CH-###/seed/]
  D --> E[Generate CHANGE.yaml + plan.md + tasks.md skeleton]
  E --> F[Create baseline tests (language-specific)]
  F --> G[Link seed artifacts to System Model Graph nodes]
  G --> H[Emit summary + next steps]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| YAML | `changes/CH-###/seed/CHANGE.yaml` | PM, IM, Implementer |
| Markdown | `changes/CH-###/seed/plan.md`, `tasks.md` | IM, Implementer, QA |
| Code/context | `changes/CH-###/seed/context/` | Implementer |
| Tests | `changes/CH-###/seed/tests/` | Tester, QA |
| Manifest links | `changes/CH-###/seed/manifest_refs.yaml` | Traceability agents |

## 6. Mockups / UI Views
- Directory tree screenshot: `artifacts/mockups/FR-40/seed_structure.png`
- CLI output example: `artifacts/mockups/FR-40/codexa_seed_output.txt`

## 6.1 Change & Traceability Links
- change_refs: `CH-003`.
- trace_sections: `TRACEABILITY.md#ws-110-change-seed-generator`, `TRACEABILITY.md#fr-40-change-seeds-with-manifeststests`.
- artifacts: `docs/CHANGE_REQUEST_003_discovery.md`, `docs/REQUIREMENTS_1_3.md`.

## 7. Acceptance Criteria
- [ ] Running `codexa seed dashboard async-refactor` creates seed directory with manifests, plan, tasks, baseline tests, and context symlinks/copies.
- [ ] Seeds reference discovery manifests via relative paths and include manifest hash snapshot.
- [ ] Baseline tests generated (or stubbed) for languages supported by CLI flag (initially Python, TypeScript, Rust).
- [ ] CHANGE.yaml captures mission summary, related FRs, dependencies, and checklist for readiness.
- [ ] Seed metadata appended to System Model Graph and traceability matrix automatically.

## 8. Dependencies
- FR-38 discovery manifests.
- FR-39 System Model Graph.
- FR-41 metrics (seed should include expected coverage baseline).
- Language-specific test scaffolding toolkits.

## 9. Risks & Assumptions
- Copying large context slices may bloat repo; use symlinks or filters for huge files.
- Language-specific test scaffolds require upkeep; stage rollout per language wave (initial: Python, TS, Rust).
- Seeds must remain deterministic; ensure CLI respects ignore patterns and pinned commit SHA.

## 9.1 Retention Notes
- Seed folders stay under `changes/CH-###/seed/`; old seeds can be archived via retention policy once change merged.

## 10. Review Status
| Field | Value |
| --- | --- |
| **Status** | Draft |
| **Reviewed By** | _Pending_ |
| **Date** | 2025-11-04 |
| **Linked Change** | CH-003 |
