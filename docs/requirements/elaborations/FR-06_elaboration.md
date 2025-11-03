---
fr_id: FR-06
ch_refs:
  - CH-002
trace_links:
  - TRACEABILITY.md#fr-06-handoff-logging
  - TRACEABILITY.md#ws-206-change-records--audit-extensions
status: Draft
---

# 🧩 Requirement Elaboration — FR-06

## 1. Summary
Capture structured handoff logs for every agent exchange, enriching audit trails with `{fr_id, ws_id, tc_id, ch_id, maturity_level, run_id, seed, raci_role, artifact_hash}` and ensuring reproducibility for the change-centric governance model.

## 2. Context & Rationale
Demonstrating auditability is core to the spike. CR002 mandates that each handoff (PM↔Designer↔Implementer↔QA↔TQA↔GO↔HR) records comprehensive metadata so reviewers can reconstruct change lifecycles, Governance Officer approvals, and Implementer retention decisions. These logs underpin FR-26 traceability, FR-27 retention audits, and `/df.*` command outputs.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| `handoff_event` | Dict event from agents | `{"from":"Implementer","to":"QA","fr_id":"FR-04","ch_id":"CH-017"}` | Raw payload generated at runtime. |
| `artifact_manifest` | JSON (`artifacts/work/CH-###/run-*/manifest.json`) | `{"files":["docs/IMPLEMENTATION_PLAN.md"],"hashes":{"...":"..."}}` | Evidence paths + hashes attached to event. |
| `maturity_state` | YAML (`PROJECT_METADATA.md`) | `maturity_level: M2` | Determines required fields (e.g., Governance Officer). |
| `approval_context` | JSONL (`artifacts/phase1/approvals/events.jsonl`) | `{"ch_id":"CH-017","status":"Partially Approved","actor":"GO"}` | Linked to handoff when approvals triggered.
| `execution_metadata` | JSON (`artifacts/work/CH-###/run-*/summary.json`) | `{"run_id":"run-2025-11-01T12:00","seed":42,"duration_ms":58234}` | Provides reproducibility info for Implementer runs.

### Edge & Error Inputs
- Missing `fr_id` or `ch_id` → log rejected with error and PM must reissue event; FR-07 concern recorded.
- Artifact hash mismatch → log entry flagged `suspect`, raise FR-07 concern, and require manual review.
- Duplicate event ID → dedupe while retaining most recent timestamp with note referencing original entry.
- Missing run metadata for Implementer → event stored but marked `incomplete`, retention triggered until metadata supplied.

## 4. Process Flow
```mermaid
flowchart TD
  A[Receive handoff_event] --> B[Validate required fields + schema version]
  B --> C[Enrich with artifact hashes + maturity + run metadata]
  C --> D[Attach approval + concern references]
  D --> E[Write JSONL (audit/handoffs.jsonl)]
  E --> F[Emit metrics + update CHANGE_SUMMARY.md references]
  F --> G[Expose via /status, `/df.*` exports, TRACEABILITY.md anchors]
```

## 5. Outputs
| Format | Example | Consumer |
|--------|---------|----------|
| JSONL | `audit/handoffs.jsonl` enriched event with `{run_id, seed}` | QA, Governance |
| Markdown | `artifacts/phase1/demo/handoff_table.md` summary referencing `CH-###` | Demo collateral |
| CSV / JSON | `artifacts/metrics/handoff_counts.csv` / `.json` with lifecycle durations | Observability tooling |
| JSONL | `audit/errors.log` for failed events with remediation guidance | PM / Governance Officer

## 6. Mockups / UI Views (if applicable)
- `artifacts/mockups/FR-06/handoff_audit_table.md` — Table used during demos.
- `artifacts/mockups/FR-06/handoff_retention.md` — Example entry showing retention flag.

## 6.1 Change & Traceability Links
- `change_refs`: `CH-002`, plus individual `CH-###` tied to logged events.
- `trace_sections`: `TRACEABILITY.md#fr-06-handoff-logging`, `TRACEABILITY.md#ws-206-change-records--audit-extensions`.
- `artifacts`: `audit/handoffs.jsonl`, `CHANGELOG.md`, `changes/CH-###/status.md`, `/df.analyze` output.

## 7. Acceptance Criteria
* [ ] Every handoff record contains `{fr_id, ws_id, tc_id?, ch_id, maturity_level, raci_role, run_id, seed, artifact_hash}` and optional approval references.
* [ ] Schema validation fails fast with actionable error message written to `audit/errors.log` and FR-07 concern logged.
* [ ] Audit file rotation keeps per-run logs ≤ 5 MB while preserving append-only history and referencing retention status.
* [ ] `/status ch-###` renders latest handoffs and `/df.checklist` verifies presence before marking change ready for approval.

## 8. Dependencies
- FR-01 orchestration (producer of handoffs), FR-04 Implementer metadata, FR-05 QA artifacts.
- FR-10 approvals to link gating decisions, FR-11 QA gating, FR-27 retention, FR-28 `/df.*` commands.
- FR-02 documentation to surface summaries, FR-26 traceability obligations.
- WS-02 audit logging primitives, WS-206 change records & audit extensions.

## 9. Risks & Assumptions
- Requires consistent time sync across agents; drift could mis-order events—mitigate with monotonic timestamps and `sequence_id`.
- High-volume logging could slow CLI; use buffered writes and incremental flush.
- Future phases will expand schema; design for forward compatibility with versioned schemas and optional fields.
- Sensitive data in logs must be scrubbed; ensure no secrets stored in artifact hashes or summaries.

## 9.1 Retention Notes
- When Implementer sets `--retain`, handoff entries must reference the retained run folder and mark `retained:true` to help Governance Officer audits.
- Purged runs require follow-up handoff entries noting purge completion for traceability.

## 10. Review Status
| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Reviewed By** | _Unassigned_ |
| **Date** | 2025-11-01 |
| **Linked Change** | CH-002 |
