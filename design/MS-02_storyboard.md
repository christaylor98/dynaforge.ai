# Storyboard — MS-02 Discovery MVP (Discovery → Change Seed → Update)

## 1. Purpose & Scope
- Trace the standard operator journey for milestone MS-02 from the initial discovery request through change seed creation and governance updates.
- Make component handoffs, generated artifacts, and external integrations explicit so we can validate coverage and identify gaps.

## 2. Actors & External Systems
| Domain | Participant | Responsibilities | Key Stores / Interfaces |
| --- | --- | --- | --- |
| Human | Operator / Stakeholder | Supplies requirement briefs, approves outputs, runs CLI commands. | CLI, Markdown intake templates |
| Coordination | Interaction Bridge | CLI shim that timestamps commands and appends them to `audit/commands.jsonl`. | Filesystem-only |
| Coordination | Project Manager Orchestrator | Validates context, sequences agents, records approvals and trace updates. | Git-tracked docs, audit logs |
| Discovery | Discovery Analyzer Agent | Runs `codexa discover`, orchestrates static tooling, writes manifests. | tree-sitter, tokei, radon, pygount; filesystem |
| Knowledge | System Model Graph Builder | Normalises manifests into YAML projections with optional ephemeral SQLite cache. | `analysis/system_model/`, in-memory / ephemeral SQLite |
| Analytics | Coverage Metrics Service | Computes understanding/readiness metrics and writes git-tracked snapshots. | `analysis/metrics/`, `/status` |
| Change Planning | Seed Planner Agent | Generates `codexa seed` packages tied to change zones and missions. | Filesystem, git metadata |
| Governance | Requirements Intelligence & Impact Evaluator | Updates traceability, readiness summaries, impact notes. | `TRACEABILITY.md`, `docs/status/` |

External dependencies kept intentionally light for MS-02: git worktree on local filesystem, command-line tooling, static analysis stack, and optional in-process SQLite caches that may be dropped between runs. All durable artifacts must be written to git-tracked locations (`analysis/`, `changes/`, `docs/`, `TRACEABILITY.md`, `audit/`).

## 3. Happy-Path Flow

### Stage 0 — Starting State
- **Human provides:** Ensure the target repository is checked out locally at the commit of interest.
- **CLI commands:**
  ```shell
  # none (manual prerequisite)
  ```
- **Agents active:** None (baseline condition).
- **Documents created/updated:** None yet; previous discovery artifacts are treated as stale until refreshed.
- **`/status` snapshot:** `discovery: not started`, `latest_manifest: n/a`, `seed: n/a`.

### Stage 1 — Optional Context Drop
- **Human provides (optional):** Either a grab-bag of individual references _or_ a single root location (`context/`, wiki export, personal notebook). The operator can also paste loose notes into an “unstructured inbox” file for automated triage.
- **CLI commands (optional):**
  ```shell
  # Attach an entire folder hierarchy
  codexa context attach ./context --label legacy-folder

  # Attach a single markdown, PDF, email export, etc.
  codexa context attach path/to/reference.md --label legacy-doc
  codexa context attach https://wiki.example.com/page --label confluence

  # Drop raw notes into the inbox for auto-triage
  codexa context ingest docs/context/inbox/unstructured.txt --label scratch-pad
  ```
- **Agents active:** Interaction Bridge records attachments; Context Ingestion helper classifies assets (text, diagrams, spreadsheets) and flags unreadable items; Project Manager indexes references for later cross-checking.
- **Documents created/updated:** `audit/context/context_sources.jsonl` captures supplied references, `docs/context/index.yaml` lists autogen context map, `artifacts/context/unparsed.log` enumerates files we could not interpret.
- **`/status` snapshot:** Lists attached context sources, `context_unparsed:<count>` when something could not be digested, and offers `/status context` for a detailed breakdown; highlights that the step is optional.

### Stage 2 — Run Discovery
- **Human provides:** Optionally edits `docs/discovery/config.yaml` to express include/exclude rules; default is full-depth (`mode: full`) with progress telemetry.
- **CLI commands:**
  ```shell
  # Ensure config exists (creates editable template on first run)
  codexa discover config --init docs/discovery/config.yaml

  # Run discovery using the config (default mode: full)
  codexa discover --config docs/discovery/config.yaml

  # Optional quick mode override when the human chooses to interrupt a long run
  codexa discover --config docs/discovery/config.yaml --mode quick
  ```
- **Agents active:** Interaction Bridge (logging), Project Manager (pre-flight validation), Discovery Analyzer (execution with streaming progress).
- **Documents created/updated:** `docs/discovery/config.yaml` (include/exclude patterns, depth, concurrency), `audit/commands.jsonl` entry, `audit/handoffs/handoff_discovery.jsonl`, scratch directory `artifacts/discovery/run-<timestamp>/`.
- **`/status` snapshot (during run):** `discovery: running`, `mode: full|quick`, `progress: <files scanned>/<total>`, `estimated_time_remaining`, with guidance on pausing or switching to quick mode if needed.

### Stage 3 — Automated Artifact Publication & Iteration Loop
- **Human provides:** No manual intervention; the system completes this stage automatically after discovery.
- **Agents active:** Discovery Analyzer finalises manifests; System Model Graph Builder, Requirements Intelligence, and Coverage Metrics Service fire automatically.
- **Documents created/updated (all git-tracked):**
  - `analysis/system_manifest.yaml`
  - `analysis/change_zones.md`
  - `analysis/intent_map.md`
  - `analysis/system_model/components.yaml`, `relationships.yaml`, `coverage.yaml`
  - `docs/requirements/derived/DR-<timestamp>.md`
  - `analysis/metrics/understanding_coverage.yaml`, `analysis/metrics/heatmap.json`
  - `docs/status/understanding_snapshot.md`
  - `artifacts/discovery/run-<timestamp>/issues.md` summarising gaps, missing context, or anomalies
  - `docs/status/iteration_log.md` (auto-appended with “Iteration #N” header, outstanding follow-ups, next recommended action)
  - `audit/handoffs/handoff_discovery.jsonl` closed with hashes, runtime, and scope metadata
- **`/status` snapshot:** `discovery: complete`, `coverage: <percentage>%`, `gaps_detected: <count>`, `next_action: review iteration_log`.
- **Iteration loop:** After each review, the human can:
  - Amend manifests/incorporate context manually (e.g., `codexa model apply docs/context/fix.yaml`).
  - Re-run discovery (`codexa discover --config docs/discovery/config.yaml`) to refresh artifacts.
  - Use `codexa followup --accept <id>` or `codexa followup --dismiss <id>` to resolve items without a full rerun.
  - Each cycle appends to `docs/status/iteration_log.md`, giving a clear history of what changed and which gaps remain.

### Stage 4 — Review Discovery Summary & Issues
- **System output:** Immediately after Stage 3, the CLI prints a consolidated “Discovery Summary” block containing:
  - Coverage snapshot (`coverage: <percentage>%`, `zones flagged: […]`).
  - Top concerns from `issues.md`.
  - “Need your help” items (unparsed context, missing dependencies, ambiguous modules).
  - Suggested next steps (e.g., “Mark data access layer as external using `codexa followup --accept issue-12`”).
- **Human provides:** Acknowledgements or decisions (accept/dismiss follow-ups, add clarifications).
- **CLI commands:** Only needed if the human chooses to act:
  ```shell
  # Accept a suggested model adjustment without re-running discovery
  codexa followup --accept issue-12

  # Log a clarification for a persistent gap
  codexa followup annotate issue-17 --note "Handled by external billing service"
  ```
- **Agents active:** Coverage Metrics Service and Requirements Intelligence own the summary; Project Manager automatically logs accepted follow-ups and schedules reruns if requested.
- **Documents created/updated:** `docs/status/iteration_log.md` updated with follow-up decisions; `analysis/system_model/` patched if `codexa followup --accept` applied adjustments.
- **`/status` snapshot:** Mirrors the CLI summary and lists unresolved follow-ups with their IDs so the human sees all outstanding work without extra commands.

### Stage 5 — Capture & Curate Human Change Inputs
- **Human provides:** Any mix of raw requirement material—emails, PDFs, chat transcripts, screenshots. All formats go through the requirement intake pipeline.
- **CLI commands:**
  ```shell
  # Attach a bundle of artifacts (any format) for triage
  codexa requirements ingest path/to/raw_inputs/ --label intake-batch-01

  # Review the AI-curated draft requirements
  codexa requirements review intake-batch-01

  # Approve or edit curated requirements
  codexa requirements approve docs/requirements/curated/REQ-<slug>.md
  ```
- **Agents active:** Requirement Curator agent normalises inputs, extracts candidate requirements, and prompts for clarification when confidence is low; Interaction Bridge logs intake; Project Manager ensures approvals are captured.
- **Documents created/updated:** `docs/requirements/curated/REQ-<slug>.md` (cleaned requirement drafts with provenance links back to raw inputs), `docs/requirements/intake/intake-batch-01/` storing raw artifacts, `analysis/system_model/` cross-references linking requirements to discovery context, `docs/status/change_journey.md` summarising rationale, `TRACEABILITY.md` transitions entries to `IN PROGRESS`.
- **`/status` snapshot:** `requirements_intake: batch-01 (2 pending questions)` with direct links to unresolved prompts; `suggested_changes` list items the system derives from discovery.

### Stage 6 — Change Consolidation, Phasing & Milestone Design
- **Human provides:** Guidance on which curated requirements form a coherent change, plus steering on rollout ordering.
- **CLI commands:**
  ```shell
  # Group curated requirements into a named change
  codexa change create CH-010 --from REQ-xxx,REQ-yyy --objective "Modernise billing pipeline"

  # Collaboratively resolve outstanding questions
  codexa change clarify CH-010 --question "Confirm scope of legacy adapters?"

  # Phase the change for rollout
  codexa change plan CH-010 --phases phase1.yaml

  # Spin up a milestone definition pulling from selected phases
  codexa milestone propose MS-02 --from change:CH-010 --rollup phases[1-2]

  # Review milestone storyboard draft (auto-generated)
  codexa milestone storyboard MS-02 --open
  ```
- **Agents active:** Change Planner groups requirements; Phase Planner balances rollout order; Milestone Designer assembles storyboard artifacts; Requirements Intelligence syncs `TRACEABILITY.md`.
- **Documents created/updated:**
  - `changes/CH-010/change_overview.md`, `plan.yaml`, `questions.md`
  - `changes/CH-010/phases/phase1.yaml` (with dependency graphs, risk notes)
  - `milestones/MS-02/definition.yaml`, `storyboard.md`, `mockups/` (CLI outputs, diagrams, screen sketches)
  - `TRACEABILITY.md` milestone section linking requirements → phases → milestone
  - Updated `docs/ARCHITECTURE.md`, `docs/TECH_STACK.md`, or other reference docs if changes impact them
- **`/status` snapshot:** `change: CH-010 (phase planning)`, `milestone: MS-02 (storyboard draft ready for review)`, `feedback_requested: storyboard`.
- **Human/system loop:** The human reviews storyboard outputs, adds feedback inline, and the Milestone Designer adjusts artifacts iteratively until accepted. This ensures understanding before code execution begins.


### Stage 7 — Plan Change Scope & Seed
- **Human provides:** Decide _what_ should run through the execution loop next—a single curated requirement, a full change package, a phase roll-up, or an entire milestone.
- **CLI commands (choose scope as needed):**
  ```shell
  # Scope selection
  codexa loop plan --requirement REQ-123
  codexa loop plan --change CH-010
  codexa loop plan --phase changes/CH-010/phases/phase1.yaml
  codexa loop plan --milestone MS-02

  # Generate the corresponding seed bundle
  codexa seed --from loop-plan --tests pytest
  ```
- **Agents active:** Project Manager confirms scope; Seed Planner packages the relevant context/tests; Interaction Bridge logs command flow.
- **Documents created/updated:** `changes/CH-###/seed/CHANGE.yaml`, `plan.md`, `tasks.md`, `context/`, `tests/`, `manifest_refs.yaml`, `audit/handoffs/handoff_seed.jsonl`.
- **`/status` snapshot:** `seed: ready` with explicit scope listing (e.g., `scope: change CH-010` or `scope: milestone MS-02`), plus outstanding approvals.

-### Stage 8 — Human Review, Architecture & Test Alignment
- **Human provides:** Free-form feedback in whatever medium is natural—paste Slack snippets, drop notes into `docs/context/inbox/review_feedback.txt`, or reply in the orchestration chat. The AI digests that signal, annotates architecture/test artifacts, and only asks for clarification when something is ambiguous.
- **System behaviour:** The orchestrator continually refreshes a living summary (`changes/CH-###/seed/REVIEW.md`) that captures scope, design deltas, test coverage, and open questions using the latest human inputs. No rigid template is required; the document mirrors the conversation in structured form for traceability.
- **CLI commands (optional helpers, not required for feedback):**
  ```shell
  # Peek at the current roll-up the AI generated
  codexa open review changes/CH-###/seed/REVIEW.md

  # When satisfied, capture approvals or explicitly request changes
  codexa approve design changes/CH-###/seed/REVIEW.md
  codexa approve tests changes/CH-###/seed/REVIEW.md
  codexa request-changes review --note "Need load-test scaffold before approval"
  ```
- **Agents active:** Designer (updates architecture docs), Tester (baseline tests), Implementer (plan review), System Manager (approval logging). Each agent incorporates the human’s unstructured comments into the appropriate artifact and flags anything that still needs clarification.
- **Documents created/updated:** `changes/CH-###/seed/REVIEW.md` (AI-authored digest with pointers back to raw human input), `docs/ARCHITECTURE.md`, design briefs under `design/`, `changes/CH-###/seed/tests/`, `changes/CH-###/seed/plan.md` annotated with approvals, `TRACEABILITY.md` evidence columns.
- **`/status` snapshot:** `architecture: pending approval` until human signs off, then flips to `ready`.

### Stage 9 — Governance & Traceability Update
- **System output:** The orchestrator automatically compiles a governance summary once approvals land. The CLI (and optional notification) surfaces:
  - `summary.md` with a concise report of what changed, evidence paths, and coverage deltas.
  - `gaps.md` listing unresolved issues, required human inputs, and proposed remediation steps with suggested commands (e.g., re-run discovery with narrower scope).
- **Human provides:** Input only if the gaps list exists—approve remediation plan, add missing context, or delegate follow-up. No commands are required unless remedial work is requested.
- **CLI helpers (when needed):**
  ```shell
  codexa followup plan --from artifacts/ms02/storyboard/gaps.md
  codexa followup accept gap-03  # acknowledge/assign fix
  ```
- **Agents active:** Requirements Intelligence (trace updates), Impact Evaluator (risk notes), Project Manager (status publication).
- **Documents created/updated:** `TRACEABILITY.md` evidence rows, `docs/status/change_journey.md`, `docs/status/impact_notes.md`, `artifacts/ms02/storyboard/summary.md`, `artifacts/ms02/storyboard/gaps.md`.
- **`/status` snapshot:** `governance: complete` when no gaps remain; otherwise `governance: attention needed (see gaps.md)` with pointers to remediation items.

### Stage 10 — Ready for Execution Loop
- **Human provides:** Approval to start execution at the granularity they choose—single requirement, change, phase, or milestone.
- **CLI commands (choose the scope that fits):**
  ```shell
  codexa loop start --from loop-plan
  ```
- **Agents active:** Project Manager triggers downstream MS-01 loop (Designer → Implementer → Tester).
- **Documents created/updated:** Execution loop audit stubs opened (`audit/handoffs/handoff_pm_designer.jsonl`, etc.).
- **`/status` snapshot:** `execution_loop: ready`, `active_seed: CH-###`, `next_agent: Designer`.

## 4. Key Checks & Open Questions
- Ensure audit schema extensions (`handoff_discovery`, `handoff_graph`, `handoff_seed`) are formalised before implementation. *(Action: internal follow-up—no human input required.)*
- Confirm lightweight orchestration state format (JSONL vs simple YAML) for tracking storyboard stages without introducing external services. *(Action: team decision—default to simple YAML unless tooling requires otherwise.)*
- Need UX decision on where governance agents write impact notes (`docs/status/impact_notes.md` vs existing doc). *(Action: pick a single location; default to `docs/status/impact_notes.md` and document it.)*
- Validate performance budget for deep discovery mode within CI/sandbox constraints. *(Action: system reports ETA/progress; humans decide whether to continue, narrow scope, or switch to quick mode.)*
