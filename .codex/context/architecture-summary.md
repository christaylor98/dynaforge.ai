# Architecture Summary

## 🧭 PROJECT ARCHITECTURE PRINCIPLES

**Inspired by Eskil Steenberg’s Systems Approach**
**Purpose:** Maintain modular, replaceable, and high-velocity architecture.
**Audience:** Humans and AI collaborating on evolving systems.

---

### ⚙️ Core Meta-Principles

* **P0 — Refine, don’t reinvent**
  Before creating or rewriting, check whether the existing structure already supports extension.
  Reuse patterns before replacing them.
  *Verification:* “Did I improve an existing interface instead of re-architecting from scratch?”

* **P1 — Preserve the Golden Path**
  Every subsystem must serve the project’s primary workflow.
  Remove or isolate anything that adds complexity without advancing that goal.
  *Verification:* “If this module disappeared, would the core flow break or improve?”

---

### 🧩 Structural Rules

* **R1 — Maintain black-box boundaries**
  Each module must be a self-contained unit exposing only a minimal, documented public API.
  No internal cross-imports or hidden dependencies.
  Shared data flows through defined interfaces only.
  *Verification:* “Can this module be replaced without breaking any others?”

* **R2 — Favor composition over modification**
  To extend or change behavior, build new modules that *compose* or *wrap* existing ones rather than altering internals.
  Composition scales, modification decays.
  *Verification:* “Did I add new behavior externally instead of editing existing code paths?”

* **R3 — One module, one purpose**
  Each module should perform one clear, isolated responsibility.
  Cross-cutting logic (logging, validation, etc.) must live in shared middleware, not in feature code.
  *Verification:* “Can I describe this module’s purpose in a single sentence?”

* **R4 — Explicit contracts, implicit freedom**
  Inside a module, design freely; across modules, rely on strict, versioned interfaces.
  Interfaces are promises — break them only with version bumps.
  *Verification:* “Does every exposed function have clear type hints, docstrings, or schemas?”

* **R5 — Observability first**
  Every critical process must emit logs or metrics that allow tracing cause and effect.
  The system should be debuggable without guesswork.
  *Verification:* “Can I see why this module made each decision?”

---

### 🧠 Behavioral Principles

* **B1 — Clarity beats cleverness**
  Code must prioritize human readability and long-term adaptability over micro-optimizations or trick constructs.
  *Verification:* “Would another engineer or AI understand this at first glance?”

* **B2 — Local autonomy, global harmony**
  Modules should operate independently but align with shared project principles (naming, data formats, patterns).
  *Verification:* “Is this consistent with the rest of the system’s design language?”

* **B3 — Explain every automation**
  Any automated or AI-generated behavior must be reproducible and explainable.
  If a decision cannot be explained, it cannot be trusted.
  *Verification:* “Could I describe why this automation behaves as it does?”

---

### 📏 Enforcement and Feedback

* **Continuous Validation Loop**

  * Lint, type, and test automatically after every change.
  * Validate architecture rules through static checks or AI-assisted audits.
  * When feedback reveals violations, **refine the module**, not the principle.

* **Version-Controlled Principles**

  * These rules evolve only through consensus and documented reasoning.
  * Changes to this file must include justification and examples.
