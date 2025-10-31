# 🧠 REQUIREMENT ELABORATION GUIDE

_Last updated: 2025-10-30 — maintained by the Requirement Elaboration Agent (RE) and Governance Officer._

---

## 🎯 Purpose
All Functional Requirements (FR-###) **must** be elaborated before implementation.  
Elaboration bridges the gap between *intent* and *execution* by producing rich, reviewable context that humans and AI can both understand.

---

## 🧩 Core Principles

1. **Every FR is elaborated** — no terse one-liners.  
2. **Human + AI alignment first** — development starts only after review approval.  
3. **Examples over prose** — show, don’t just describe.  
4. **Reusable format** — same structure across phases and projects.  
5. **Living document** — elaborations evolve through Change Management (`CH-###`).

---

## 🧱 File Location & Naming

Each elaboration lives in its own file under:

```

/docs/requirements/elaborations/FR-###_elaboration.md

````

The file is version-controlled and linked from the Traceability Matrix.

---

## 📄 Standard Structure


# 🧩 Requirement Elaboration — FR-###

## 1. Summary
Short, plain-language description of the feature or behaviour.

## 2. Context & Rationale
Why this requirement exists, what user or system goal it serves, and how it aligns with the project vision.

## 3. Inputs
| Name | Type / Format | Example | Notes |
|------|----------------|---------|-------|
| param | JSON | `{"symbol":"NAS100_USD"}` | Source API request |
| config | YAML | `risk_limit: 0.02` | Strategy configuration |

### Edge & Error Inputs
Examples of invalid or boundary cases and required system response.

## 4. Process Flow
Use Mermaid or simple pseudocode to show sequence and logic.

```mermaid
flowchart TD
  A[Receive Input] --> B[Validate]
  B -->|ok| C[Process]
  B -->|fail| D[Log Error]
  C --> E[Return Output]
````

## 5. Outputs

| Format   | Example                                | Consumer     |
| -------- | -------------------------------------- | ------------ |
| JSON     | `{"signal":"BUY","confidence":0.72}`   | Trader Agent |
| Markdown | `/artifacts/reports/signal_summary.md` | Dashboard    |

## 6. Mockups / UI Views (if applicable)

Link or embed screenshots, wireframes, or quick sketches:
`/artifacts/mockups/fr###_ui.png`

## 7. Acceptance Criteria

Concrete, testable statements of success.

* [ ] Valid input → correct output in <200 ms
* [ ] Invalid input → error logged with code E104
* [ ] Meets UX spec `MOCK-013`

## 8. Dependencies

List related FRs, WSs, APIs, or data models.

## 9. Risks & Assumptions

Identify uncertainties, external dependencies, and mitigation notes.

## 10. Review Status

| Field             | Value                                           |
| ----------------- | ----------------------------------------------- |
| **Status**        | Draft / Under Review / Approved / Rework Needed |
| **Reviewed By**   | Human Reviewer Name                             |
| **Date**          | YYYY-MM-DD                                      |
| **Linked Change** | CH-### if derived from a change                 |



---

## 🧭 Elaboration Lifecycle

```mermaid
flowchart TD
  DRAFT[✏️ Draft FR] --> RE[🧠 Requirement Elaboration Agent]
  RE --> HR[👤 Human Reviewer]
  HR -->|Approve| PM[🧭 Project Manager]
  HR -->|Rework| RE
  PM --> IM[🧱 Implementation Manager]
  IM --> QA[🧪 QA Auditor]
````

**Rules**

* Implementation Manager **cannot** create workstreams for an FR until its elaboration is *Approved*.
* Any update to an elaboration automatically triggers a **Change Evaluation** and version bump.

---

## 🧠 Agent Responsibilities

| Agent                                  | Key Actions                                                                  |
| -------------------------------------- | ---------------------------------------------------------------------------- |
| **Requirement Elaboration Agent (RE)** | Generate/update elaboration docs, including examples, diagrams, and mockups. |
| **Human Reviewer (HR)**                | Validate clarity, intent, and completeness. Add examples or visuals.         |
| **Governance Officer (GO)**            | Enforce “elaboration-before-implementation” rule.                            |
| **Project Manager (PM)**               | Link approved elaborations to Traceability Matrix.                           |
| **Implementation Manager (IM)**        | Decompose only approved elaborations into WS tasks.                          |
| **QA Auditor (QA)**                    | Derive initial test skeletons from examples and acceptance criteria.         |

---

## ⚙️ Automation Hooks

* **Detection:** PM agent scans `/docs/requirements` for new FRs → assigns RE agent.
* **Validation:** GO agent blocks FRs with `review_status != Approved`.
* **Change Propagation:** Updated elaborations trigger IA + CE agents to reassess impact and ROI.
* **Testing:** QA agent parses “Inputs / Outputs / Acceptance Criteria” to auto-seed test cases.

---

## 🧩 Review Guidance for Humans

Before approving an elaboration, confirm:

1. You could build or test this feature **without further clarification**.
2. Examples reflect realistic data and edge cases.
3. Acceptance criteria are measurable and unambiguous.
4. Visuals or flows make the logic understandable at a glance.
5. Dependencies and risks are explicitly listed.

---

## 📈 Maturity Expectations

| Maturity | Elaboration Depth                                           | Review Rigour               |
| -------- | ----------------------------------------------------------- | --------------------------- |
| **M0**   | Full elaboration for all spike FRs (sketches acceptable).   | Single human review.        |
| **M1**   | Full elaboration with concrete examples & flows.            | Human review + PM sign-off. |
| **M2+**  | Same structure, formal review, traceability links enforced. | GO approval required.       |

---

## ✅ Benefits Recap

* Eliminates AI ↔ human misunderstandings early.
* Produces review-ready specifications before code.
* Enables QA automation directly from examples.
* Serves as living documentation for future maintenance.

---

*End of Guide*
