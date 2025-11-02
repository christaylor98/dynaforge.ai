# Change Ideas 002 Requirement Impact

## Context
- `CH-001` proposes a change-centric governance model anchored on `CH-###` objects with bidirectional propagation, staged approvals, and lifecycle states.
- `CH-002` embeds an ephemeral spec-plan-task loop inside the Implementer with transient workspaces, durable outputs, and structured commands.
- `CH-003` adds Codexa doctor and analysis commands to validate traceability and health prior to implementation.
- `CH-004` applies SpekKit-style decomposition discipline to the Implementer micro-loop with deterministic execution and cleanup.
- Collectively these changes target the Implementer, governance, and QA pathways to handle change tracking, auditability, and reproducibility.

## Updated Requirements
| Requirement ID | Current Focus | Required Update from Change Ideas 002 | Source Change Idea |
| --- | --- | --- | --- |
| FR-04 | Implementation governance coordinates plan→task execution across agents. | Require every execution path to originate from a `CH-###` change anchor, enforce the SpekKit-style micro-spec loop, and integrate staged approval handling within Implementer runs. | CH-001, CH-002, CH-004 |
| FR-06 | Audit trails capture structured hand-offs and evidence. | Link audit events to change IDs, record reproducibility metadata (tool versions, seeds, timestamps), and persist Implementer run logs in `artifacts/work/`. | CH-002 |
| FR-07 | Concern management escalates drift and QA gaps. | Extend concern handling to raise rework loops on failed Implementer runs, ensure `/df.clarify` and `/df.analyze` surface traceability gaps, and align with change-centric reconciliation guarantees. | CH-001, CH-003 |
| FR-11 | QA policy gates merges based on QA verdicts. | Incorporate Implementer micro-task verdicts, enforce `/df.checklist` gating, and accommodate staged/partial approvals tied to change objects. | CH-002, CH-004 |

## New Requirements
| Proposed ID | Requirement Summary | Primary Owner | Motivation from Change Ideas 002 |
| --- | --- | --- | --- |
| FR-25 (proposed) | Provision dedicated `changes/CH-###/` workspaces with `spec.md`, `plan.md`, `tasks.md`, `impact.md`, `evidence.json`, and `status.md` to keep every change synchronized. | Governance Officer / Implementation Manager | CH-001 Change Workspace Convention |
| FR-26 (proposed) | Maintain bidirectional traceability that maps each FR/WS/TC to at least one `CH-###` and vice versa, including lifecycle state tracking. | Governance Officer | CH-001 Traceability Clause & Lifecycle |
| FR-27 (proposed) | Manage ephemeral Implementer workspaces under `artifacts/work/CH-###/run-*`, retaining outputs on failure and purging on success while recording structured audit JSON. | Implementer | CH-002 Ephemeral Workspaces & Durable Outputs |
| FR-28 (proposed) | Provide `/df.clarify`, `/df.analyze`, `/df.checklist`, and `codexa doctor` commands that emit JSON logs for preflight health checks. | QA Lead / Tooling | CH-003 Command Set |
| FR-29 (proposed) | Enforce Implementer micro-task decomposition with deterministic sequencing, evidence capture, and automatic cleanup once approvals complete. | Implementer | CH-004 Micro-Spec Loop |

## Traceability, Audit, and Artifact Updates
- **Change Object Primacy:** All artifacts and approvals reference a `CH-###`; reconciliation rules detect drift and drive rework loops instead of resets.
- **Workspace Layout:** Standardize the durable `changes/CH-###/` bundle and ephemeral `artifacts/work/CH-###/run-*` runs, ensuring `.gitignore` coverage and retention flags for diagnostics.
- **Lifecycle & Approvals:** Track Draft → Analyzed → In-Progress → Partially Approved → Approved → Merged states, enabling staged approvals and partial denials routed through FR-07 concern loops.
- **Implementer Flow:** `/change.new` anchors the work, `/implement` executes the micro-loop with deterministic seeds, streaming audit events, and post-run `/df.checklist` gating before `/approve`.
- **Audit Evidence:** Emit JSON/JSONL artifacts (`evidence.json`, `audit events`, `artifacts/analyze/`) tagged with `{ ch_id, step, files, tests, duration_ms, seed }` to support reproducibility and traceability coverage metrics.
- **Clipped Document Convention:** Introduce `_c_<filename>.md` renaming for design or ideation docs that have been incorporated into baseline artifacts. Prefixed files act as archived context, excluded from active agent sweeps, and can carry YAML footers summarizing incorporation paths and dates.

### Clipped Documents Governance Addendum
| Aspect | Benefit |
| --- | --- |
| Traceability | Closing the loop between ideation and baseline artifacts becomes verifiable at a glance. |
| Visual Clarity | Folder scans separate active vs archived work without relocations. |
| Automation | Build and lint tooling can ignore `_c_*` files while still surfacing unclipped work. |
| Provenance | No deletion of historical reasoning, aiding audits and retrospectives. |
| Flow Discipline | Reinforces the idea→design→architecture→implementation progression by marking completion. |

**Process Convention**
- Active documents retain their original filenames (e.g., `design_microservices.md`).
- Once content is fully incorporated, prepend `_c_` to mark it clipped (e.g., `_c_design_microservices.md`).
- Tooling additions:
  - Add `_c_*` patterns to `.specignore`, `.codexignore`, and `codexa.yaml` to keep clipped docs out of active scans.
  - Optional `codexa clip` helper automates renaming, appends a YAML footer, and logs provenance to `TRACEABILITY.md` under “Source Documents”.
- Optional YAML footer for clipped docs:
  ```yaml
  ---
  status: clipped
  incorporated_into:
    - docs/requirements.md
    - docs/traceability.md
  date_clipped: 2025-11-01
  ```

## Follow-ups / Resolutions
- **Ownership Split:** Governance Officer owns lifecycle enforcement (state transitions, approval gates, reconciliation checks) while the Implementation Manager maintains the durable `changes/CH-###/` bundle, updates `status.md`, and ensures Implementer runs register against the active change. Weekly sync between the two roles confirms state accuracy before HR approvals.
- **Ephemeral Retention Policy:** Successful Implementer runs are auto-purged when older than 48 hours or when space usage under `artifacts/work/` exceeds 2 GB, whichever comes first. Failed runs persist for 30 days. The `--retain` flag writes a `.retain` marker in the run folder so cleanup skips it until the marker is removed manually, keeping the policy simple but space-aware.
- **Audit Event Schema:** Adopt a normalized JSONL schema with fields `{ ch_id, run_id, lifecycle_state, event_type, actor, timestamp, status, step, fr_refs[], ws_refs[], tc_refs[], files[], metrics{ duration_ms, assertions, coverage }, seed, command, notes }`. `/df.*` commands emit entries with `event_type` values such as `df.clarify.summary` and populate `metrics` with coverage/drift counts so FR-06 ingestion can treat all audit logs uniformly.
- **Staged Approval Alignment:** Implementer transitions `status.md` to `Partially Approved` once IM and QA checks pass; Governance Officer consumes the audit feed to mark `Approved`, and HR performs final merge authorization. Any denial at Governance or HR reopens the change via an FR-07 concern, ensuring the staged flow mirrors existing approval handoffs without bypassing HR.
- **SpekKit-Inspired Loop Design:** Reimplement the micro-task engine with three modules—`planner` (derives micro-spec/tasks per CH, seeded for determinism), `executor` (runs tasks, captures diffs/tests, posts audit events), and `cleanup` (applies retention rules, updates lifecycle). Interfaces expose adapters so future heuristic upgrades replace the planner without reworking executor logic, satisfying FR-29 without importing SpekKit code.
