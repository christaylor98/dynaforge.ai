# Phase 1 Brief — Concern Lifecycle Integration

## Objective
Implement concern lifecycle mirroring, lifecycle commands, and QA enforcement gates.

## Context
Phase 0 established the repository skeleton and logging primitives. Phase 1 must now operationalize the full agent loop with concern tracking, human approvals, and policy enforcement.

## Focus Areas
- Mirror concern entries from JSONL into Markdown summaries.
- Extend CLI interaction stub with lifecycle commands (/ack, /resolve, /assign, /pause, /resume, /promote).
- Integrate QA policy enforcement prior to promotions.
- Provide status snapshots exposing open concerns and QA posture.

## Deliverables
- Phase 1 brief, design spec, implementation plan, and QA plan.
- `make phase1-demo` executing orchestrated workflow.
- Artifacts under `artifacts/phase1/` evidencing the loop.

## Success Metrics
- Concern lifecycle documented and observable in Markdown + JSONL.
- Interaction stub returns deterministic payloads for lifecycle commands.
- QA policy enforcement blocks promotion when thresholds fail.

## Next Actions
- Designer: translate objective into architecture and interaction flow.
- Implementer: prepare execution plan aligned with design decisions.
- Tester: define validation scenarios tied to success metrics.
