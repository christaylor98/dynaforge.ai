# 🧩 Requirement Elaboration — FR-06

## 1. Summary
Capture structured handoff logs for every agent exchange in MS-01, enriching audit trails with requirement, workstream, and change metadata.

## 2. Context & Rationale
Demonstrating auditability is core to the spike. FR-06 ensures each handoff (PM↔Designer↔Implementer↔Tester) records the who/what/why in a machine- and human-readable format so reviewers can reconstruct the loop and QA can derive tests automatically.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `handoff_event` | Dict event from agents | `{"from":"Designer","to":"Implementer","fr_id":"FR-03"}` | Raw payload generated at runtime. |
| `artifact_manifest` | JSON (`artifacts/phase1/manifest.json`) | `{"files":["design/DESIGN_SPEC.md"]}` | Evidence paths attached to event. |
| `maturity_state` | YAML (`PROJECT_METADATA.yaml`) | `maturity_level: M0` | Determines required fields. |
| `approval_context` | JSONL (`artifacts/phase1/approvals/events.jsonl`) | `{"change_id":"CH-001","status":"approved"}` | Linked to handoff when approvals triggered. |

### Edge & Error Inputs
- Missing `fr_id` → log rejected with error and PM must reissue event.
- Artifact hash mismatch → raise concern and mark event as `suspect`.
- Duplicate event ID → dedupe while retaining most recent timestamp.

## 4. Process Flow
```mermaid
flowchart TD
  A[Receive handoff_event] --> B[Validate required fields]
  B --> C[Enrich with artifact hashes + maturity]
  C --> D[Append approval links if present]
  D --> E[Write JSONL record]
  E --> F[Emit metrics (counts, durations)]
  F --> G[Expose via /status + audit exports]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| JSONL | `audit/handoffs.jsonl` enriched event | QA, Governance |
| Markdown | `artifacts/phase1/demo/handoff_table.md` summary | Demo collateral |
| Metrics | `artifacts/metrics/handoff_counts.csv` | Observability tooling |

## 6. Mockups / UI Views (if applicable)
- `artifacts/phase1/screenshots/handoff_audit_table.md` — Table used during demos.

## 7. Acceptance Criteria
* [ ] Every handoff record contains `{fr_id, ws_id, tc_id?, change_id, maturity_level, raci_role}`.
* [ ] Schema validation fails fast with actionable error message written to `audit/errors.log`.
* [ ] Audit file rotation keeps per-run logs ≤ 5 MB while preserving append-only history.
* [ ] `/status` renders latest three handoffs for quick verification.

## 8. Dependencies
- FR-01 orchestration (producer of handoffs).
- FR-10 approvals to link gating decisions.
- FR-02 documentation to surface summaries.
- WS-02 audit logging primitives, WS-07 demo workflow preparation.

## 9. Risks & Assumptions
- Requires consistent time sync across agents; drift could mis-order events.
- High-volume logging could slow CLI; ensure buffered writes.
- Future phases will expand schema; design for forward compatibility with optional fields.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-10-30 |
| **Linked Change** | Pending |
