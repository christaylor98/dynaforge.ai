# Agents RACI Matrix

## Purpose
This document consolidates the accountability model for the Code Overlord agent ecosystem after Change Requests `CR001 → CR001.3` and requirements update `REQUIREMENTS_1_1`. It establishes a single reference for who is **Responsible, Accountable, Consulted,** and **Informed (RACI)** across the major workflows so prompts, audit metadata, and governance tooling remain consistent.

## Agent Roster
| Agent | Core Focus | Primary Artifacts / Signals |
| --- | --- | --- |
| Project Manager (PM) | Orchestrates RA→IA→IM→QA→TQA→GO loop, maintains requirements/status docs, drives change objects and metrics, applies maturity rules. | `REQUIREMENTS.md`, `PROJECT_OVERVIEW.md`, `PROJECT_DETAIL.md`, `CHANGELOG.md`, dashboards |
| Implementation Manager (IM) | Decomposes objectives into `WS-*`, tracks execution evidence, coordinates implementation throughput. | `IM_PROGRESS.md`, workstream tables |
| Governance Officer (GO) | Oversees QA/TQA outputs, maturity gate reviews, compliance evidence, and approval workflows. | `GOVERNANCE_REPORT.md`, audit JSONL, maturity review notes |
| Requirements Analyst (RA) | Detects requirement deltas, refreshes traceability, generates impact summaries. | Traceability matrix, requirement notes |
| Impact Assessor (IA) | Quantifies downstream effects, maintains `IMPACT_REPORT.md`, flags ripple risks. | `IMPACT_REPORT.md`, WS/FR annotations |
| Requirement Elaboration Agent (RE) | Drafts and updates FR elaboration files, coordinates with reviewers, ensures acceptance criteria/examples captured. | `docs/requirements/elaborations/FR-###_elaboration.md` |
| Designer | Produces and updates system architecture and interface specifications. | `design/ARCHITECTURE.md`, `design/DESIGN_SPEC.md` |
| Implementer | Delivers code artifacts aligned to design and workstream scope, with structured handoffs. | Code branches, handoff records |
| Test Synthesizer (TS) | Generates or updates `TC-*` suites in response to change/coverage gaps. | Test sources, traceability links |
| Tester | Executes deterministic QA runs and captures results for policy evaluation. | `tests/TEST_PLAN.md`, `tests/TEST_RESULTS*.md` |
| QA Auditor (QA) | Validates FR↔WS↔TC linkage, produces traceability gap reports, enforces status updates. | `TRACE_AUDIT.md`, traceability matrix |
| Test Quality Assessor (TQA) | Rates coverage depth vs risk tiers and maturity expectations, advising QA gates. | Test Quality Summary tables |
| Change Evaluator (CE) | Produces ROI/disruption recommendations for `CH-###` records (advisory). | `CHANGE_EVALUATION.md`, change object notes |
| Vision Validator (VV) | Confirms proposed changes remain aligned with the mission and architecture. | Vision alignment comments, CE inputs |
| Human Reviewer (HR) | Holds ultimate approval authority for plans, high-impact changes, and phase promotions. | Inline approvals, release sign-offs |

## Requirements & Planning
| Activity | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) |
| --- | --- | --- | --- | --- |
| Requirements intake & decomposition | RA | IM | PM, IA | GO, QA, Designer, Implementer |
| Requirement elaboration authoring | RE | GO | PM, RA, HR | IM, QA |
| Requirement elaboration approval & linkage | HR | GO | PM, RE | IM, QA, CE |
| Traceability maintenance & updates | QA | GO | RA, IM, TQA | PM, HR |
| Workstream planning & scheduling | IM | PM | RA, IA, Designer | GO, QA, TQA |
| Architecture specification | Designer | PM | RA, IM, Implementer | GO, QA |

## Change & Impact Management
| Activity | R | A | C | I |
| --- | --- | --- | --- | --- |
| Change object creation (`CH-###`) & log maintenance | PM | GO | IM, CE, IA | HR, QA, TQA |
| Impact analysis & ripple mapping | IA | IM | RA, QA, TQA | PM, GO |
| Change evaluation (ROI vs disruption) | CE | GO | IA, PM, VV | HR, IM |
| Vision alignment check | VV | PM | CE, Designer | GO, HR |
| Partial approval handling inside change record | PM | GO | IM, IA, CE | HR |
| Elaboration update → change trigger | RE | GO | PM, IA, CE | IM, QA, TQA |

## Delivery Execution
| Activity | R | A | C | I |
| --- | --- | --- | --- | --- |
| Work package implementation | Implementer | IM | Designer, QA, TS | PM, GO |
| Test generation / maintenance | TS | QA | TQA, IA | IM, PM |
| Test execution & results capture | Tester | QA | TQA, TS | GO, PM |
| Code/design handoff logging | Implementer | PM | Designer, QA | GO, HR |

## Quality & Maturity Assurance
| Activity | R | A | C | I |
| --- | --- | --- | --- | --- |
| Traceability gap detection & reporting | QA | GO | RA, IM, TQA | PM, HR |
| Risk-tier depth assessment | TQA | GO | QA, TS | PM, HR |
| QA policy enforcement before merge | QA | GO | TQA, PM, IM | HR |
| Maturity metadata upkeep (`PROJECT_METADATA`) | PM | GO | RA, QA, TQA | All agents, HR |
| Maturity gate review & upgrade recommendation | GO | PM | QA, TQA, CE, VV | HR, IM |
| Elaboration compliance check (Approved-before-WS) | GO | PM | RE, HR, IM | QA, CE |

## Governance & Approvals
| Activity | R | A | C | I |
| --- | --- | --- | --- | --- |
| Status & metrics snapshot publication | PM | PM | GO, IM, QA, TQA | HR, all agents |
| Compliance & audit evidence bundle | GO | PM | QA, PM, CE | HR |
| Promotion / release readiness submission | GO | PM | QA, TQA, CE, VV | HR, IM |
| Final promotion / phase approval | HR | HR | PM, GO | All agents |

## Usage Notes
- RACI assignments are **advisory**: agents may collaborate freely, but handoff metadata and audit logs must reflect the roles defined here (see `FR-20`, `FR-25`, `FR-35` in `REQUIREMENTS_1_1.md`).
- Maturity level from `PROJECT_METADATA.md` can modulate enforcement (e.g., QA/TQA involvement at M0 is optional); use the same RACI structure but deactivate roles not required at the current level.
- Requirement elaborations should carry `responsible=RE`, `accountable=GO`, and `reviewed_by=HR` metadata when capturing approvals.
- RACI tags written into audit JSONL should use lowercase `responsible`, `accountable`, `consulted`, `informed` fields referencing the agent identifiers above.
