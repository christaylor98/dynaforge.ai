# Maturity Levels (Initial Draft)

This guide introduces the first three maturity tiers for Dynaforge.ai, derived from Change Requests `CR001 → CR001.3` and the consolidated requirements in `REQUIREMENTS_1_1.md`. Each level describes the minimum processes, artifacts, and agent involvement expected before advancing to the next tier.

## Level M0 — POC / Spike Delivery
- **Purpose:** Ship a thin vertical proof-of-concept that demonstrates core value with minimal ceremony.
- **Agent involvement:**
  | Agent | Role at M0 |
  | --- | --- |
  | Project Manager (PM) | Coordinates spike scope, captures objectives, minimal governance. |
  | Implementation Manager (IM) | Breaks down spike tasks, tracks ad-hoc evidence. |
	  | Designer | Delivers just-enough architecture guidance. |
	  | Requirement Elaboration (RE) | Drafts spike-level elaborations and captures rapid feedback for HR review. |
  | Implementer | Builds POC functionality, logs lightweight handoffs. |
  | Test Synthesizer (TS) | Generates/updates tests for newly identified coverage gaps. |
	  | Requirement Elaboration (RE) | Maintains elaboration documents as changes land; coordinates HR approval. |
	  | Tester | Executes defined test suites and records results. |
  | Other agents (RA, IA, QA, etc.) | Not engaged or purely advisory on request. |
- **Core processes:**
  - Capture objectives in `REQUIREMENTS.md` and track progress in `PROJECT_DETAIL.md`, targeting a demo-quality deliverable.
  - Record handoffs via basic JSONL logging; structured change objects remain optional.
  - Run manual QA sanity checks focused on the demo path; traceability is lightweight.
- **Deliverables:** Working POC build, demo instructions, baseline audit logs.
- **Promotion criteria (informal):** POC build accepted by human reviewer; clear appetite to iterate toward Beta.

## Level M1 — Beta Delivery
- **Purpose:** Produce a feature-complete Beta release with emerging governance and repeatable quality.
- **Agent involvement:**
  | Agent | Role at M1 |
  | --- | --- |
  | PM & IM | Continue to coordinate workstreams and documentation with increased cadence. |
  | Requirements Analyst (RA) | Actively monitors requirement changes and updates traceability skeleton. |
  | Impact Assessor (IA) | Runs impact analysis for requirement/doc deltas. |
  | Test Synthesizer (TS) | Generates/updates tests for newly identified coverage gaps. |
  | Tester | Executes defined test suites and records results. |
  | QA Auditor | Provides advisory traceability checks (partial coverage acceptable). |
  | Designer & Implementer | Maintain Beta-ready architecture/code. |
  | Other agents (GO, TQA, CE, VV) | Optional / limited involvement; may consult as needed. |
- **Processes added:**
  - Generate change objects (`CH-###`) with summaries in `CHANGELOG.md` for every noteworthy decision.
  - Run RA→IA loop on requirement/doc changes; IM tracks execution in `IM_PROGRESS.md`.
  - Stand up FR↔WS↔TC skeleton with risk tier tags and Test Quality Summary tables.
  - Execute sunny-day and edge-path tests; Tester captures results; QA gate gives advisory go/no-go.
- **Deliverables:** Beta build, change log, updated traceability skeleton, documented test evidence, preliminary metrics snapshot.
- **Promotion criteria:** Beta accepted by stakeholders; change objects maintained; QA/traceability skeleton operating reliably.

## Level M2 — Governed Release
- **Purpose:** Deliver a fully governed, general-release product with compliance-grade evidence.
- **Agent involvement:**
  | Agent | Role at M2 |
  | --- | --- |
  | PM & IM | Operate full governance loop, integrate metrics/approvals. |
  | RA & IA | Fully active; maintain traceability and impact reporting with zero gaps. |
  | Designer & Implementer | Deliver production-ready architecture and implementation with documented handoffs. |
  | QA Auditor | Enforces traceability, gaps must be resolved. |
  | Test Synthesizer & Tester | Maintain full suites aligned to risk tiers and release criteria. |
  | TQA | Evaluates coverage depth; feeds QA policy compliance. |
  | Governance Officer (GO) | Oversees compliance, maturity reviews, approvals. |
  | Change Evaluator (CE) | Supplies ROI/disruption guidance for decisions. |
	  | Requirement Elaboration (RE) | Keeps elaborations in sync with released scope; ensures change hooks trigger CE/IA. |
	  | Vision Validator (VV) | Confirms alignment before major changes. |
  | Human Reviewer (HR) | Issues final release approval. |
- **Processes added:**
  - Enforce multi-gate change approvals (IA → CE → GO → PM → HR) with partial approval tracking.
  - Require traceability gap reports, risk-depth assessments, and maturity metadata in `PROJECT_METADATA.md`.
  - QA policy blocks merges unless coverage, ROI guidance, and maturity criteria satisfied.
  - Publish status snapshots and dashboards with change density, change-to-delivery lag, vision drift, stability ratio.
- **Deliverables:** Hardened release build, signed governance report, full traceability matrix, QA/TQA evidence bundle, maturity metadata, change evaluation records.
- **Promotion criteria:** All FRs have validated trace links; QA/TQA gates pass; Governance Officer and Human Reviewer sign off for production rollout (future M3+ to cover continuous optimization).

---

**Usage:** Agents read `PROJECT_METADATA.md` to determine the active maturity level and enable or skip processes accordingly (see `FR-35` in `REQUIREMENTS_1_1.md`). This document will expand as additional tiers (M3, M4) are defined.
