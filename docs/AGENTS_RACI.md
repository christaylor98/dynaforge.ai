# Agents RACI Matrix

## Purpose
This document consolidates the accountability model for the Codexa.ai agent ecosystem after Change Requests `CR001 → CR003` and requirements update `REQUIREMENTS_1_3`. It establishes a single reference for who is **Responsible, Accountable, Consulted,** and **Informed (RACI)** across the major workflows so prompts, audit metadata, and governance tooling remain consistent.

## Agent Roster
| Agent | Core Focus | Primary Artifacts / Signals |
| --- | --- | --- |
| Project Manager (PM) | Orchestrates RA→IA→IM→QA→TQA→GO loop, maintains requirements/status docs, drives change objects and metrics, applies maturity rules, and runs the MS-02 loop-planning conversation that feeds execution scope into `loop-plan.json`. | `REQUIREMENTS.md`, `PROJECT_OVERVIEW.md`, `PROJECT_DETAIL.md`, `CHANGELOG.md`, dashboards, `loop-plan.json` |
| Implementation Manager (IM) | Decomposes objectives into `WS-*`, tracks execution evidence, coordinates implementation throughput. | `IM_PROGRESS.md`, workstream tables |
| Governance Officer (GO) | Oversees QA/TQA outputs, maturity gate reviews, compliance evidence, and approval workflows. | `GOVERNANCE_REPORT.md`, audit JSONL, maturity review notes |
| Requirements Analyst (RA) | Detects requirement deltas, refreshes traceability, generates impact summaries. | Traceability matrix, requirement notes |
| Impact Assessor (IA) | Quantifies downstream effects, maintains `IMPACT_REPORT.md`, flags ripple risks. | `IMPACT_REPORT.md`, WS/FR annotations |
| Requirement Elaboration Agent (RE) | Drafts and updates FR elaboration files, coordinates with reviewers, ensures acceptance criteria/examples captured. | `docs/requirements/elaborations/FR-###_elaboration.md` |
| Discovery Analyzer (DA) | Runs discovery flows, generates structural/intent manifests, refreshes System Model Graph projections, and records iteration follow-ups. | `analysis/system_manifest.yaml`, `analysis/change_zones.md`, `analysis/intent_map.md`, System Model Graph YAML, `docs/status/iteration_log.md` |
| Seed Planner (SP) | Consumes `loop-plan.json` and produces scoped seed bundles (`codexa seed --from loop-plan`) with context slices, manifests, and baseline tests. | `changes/CH-###/seed/`, discovery manifests |
| Interaction Bridge (IB) | Normalises natural-language prompts (approvals, follow-ups, loop planning) into agent directives while preserving CLI aliases for deterministic playback. | `/audit/commands.jsonl`, conversation transcripts |
| Analytics Lead (AN) | Tracks understanding coverage and change readiness metrics, updates `/status` dashboards. | Status snapshots, metrics exports, discovery telemetry |
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

## Discovery & Understanding
| Activity | R | A | C | I |
| --- | --- | --- | --- | --- |
| Context ingestion & classification | DA | PM | RA, IM | GO, QA, Designer |
| Discovery pipeline execution & manifest publication | DA | PM | RA, IM, IA, AN | GO, QA, Designer, Implementer |
| System Model Graph YAML maintenance | DA | PM | RA, IA, AN | GO, QA, IM |
| Loop planning conversation (`codexa loop plan` prompt) | PM | HR | IM, DA, SP | GO, QA, IA |
| Seed generation (`codexa seed --from loop-plan`) | SP | IM | PM, DA, Designer, Implementer | GO, QA, IA |
| Understanding coverage & readiness reporting | AN | PM | GO, QA, RA, IA | HR, all agents |

## Change & Impact Management
| Activity | R | A | C | I |
| --- | --- | --- | --- | --- |
| Change object creation (`CH-###`) & log maintenance | PM | GO | IM, CE, IA | HR, QA, TQA |
| Impact analysis & ripple mapping | IA | IM | RA, QA, TQA | PM, GO |
| Change evaluation (ROI vs disruption) | CE | GO | IA, PM, VV | HR, IM |
| Vision alignment check | VV | PM | CE, Designer | GO, HR |
| Partial approval handling inside change record | PM | GO | IM, IA, CE | HR |
| Elaboration update → change trigger | RE | GO | PM, IA, CE | IM, QA, TQA |
| Conversational follow-up management (iteration log) | PM | GO | DA, AN | HR, QA |

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
| Status & metrics snapshot publication | PM | PM | GO, IM, QA, TQA, AN | HR, all agents |
| Governance summary prompt & publication | PM | GO | IA, QA, TQA, CE | HR, IM |
| Compliance & audit evidence bundle | GO | PM | QA, PM, CE | HR |
| Promotion / release readiness submission | GO | PM | QA, TQA, CE, VV | HR, IM |
| Final promotion / phase approval | HR | HR | PM, GO | All agents |

## Usage Notes
- RACI assignments are **advisory**: agents may collaborate freely, but handoff metadata and audit logs must reflect the roles defined here (see `FR-20`, `FR-25`, `FR-35`, `FR-38`–`FR-41` in `REQUIREMENTS_1_3.md`).
- Discovery cadence recorded in `PROJECT_METADATA.md` should be coordinated between PM and DA so manifests stay fresh ahead of change planning.
- Maturity level from `PROJECT_METADATA.md` can modulate enforcement (e.g., QA/TQA involvement at M0 is optional); use the same RACI structure but deactivate roles not required at the current level.
- Requirement elaborations should carry `responsible=RE`, `accountable=GO`, and `reviewed_by=HR` metadata when capturing approvals.
- RACI tags written into audit JSONL should use lowercase `responsible`, `accountable`, `consulted`, `informed` fields referencing the agent identifiers above, including discovery roles (e.g., `responsible: da` for manifest generation).
