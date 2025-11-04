# Tech Stack Overview

## Interfaces
- **Conversational Bridge:** Prompt-first interface (CLI + chat adapters) translating natural language into agent directives
- **CLI Aliases:** Deterministic commands (e.g., `codexa discover`, `codexa loop plan`) for playback and scripting

## Backend
- **Language:** Python 3.12
- **Web Framework:** FastAPI
- **API Spec:** OpenAPI 3.1
- **ORM:** SQLAlchemy 2.0
- **Caching:** Redis
- **Database:** PostgreSQL 11 (primary)
- **Analytics:** DuckDB + Parquet
- **Messaging:** Lightweight websocket layer (optional) riding on the interaction bridge
- **Service Orchestration:** systemd timers + rsync-based ingestion
- **Static Analysis / Discovery Toolkit:** tree-sitter parsers, tokei, radon, pygount

## Infrastructure
- **OS:** Debian 12
- **Containerization:** Podman
- **Networking:** ZeroTier
- **Firewall:** firewalld with segregated SSH zone

## AI & Automation
- **Agent Framework:** Codex MCP
- **Model:** GPT-5
- **IDE Assistants:** Cursor, Windsurf, Copilot
- **Testing Agents:** Spekkit-like pipelines
- **Discovery Loop:** `codexa discover --config .codexa/config.yaml` with iteration telemetry and conversational follow-up handling
- **Loop Planning & Seeds:** `codexa loop plan`, `codexa seed --from loop-plan`, prompt-first approvals (`approve design for CH-010`, `publish governance report`) with optional CLI aliases
- **Knowledge Store:** Repo-tracked YAML projections (`.codexa/manifests/system_manifest.yaml`, `.codexa/manifests/change_zones.md`, `.codexa/manifests/intent_map.md`, `.codexa/manifests/system_model/`) plus iteration logs and review digests
- **Configuration Validation:** `codexa doctor config` (FR-44) linting for `.codexa/` scaffolding with inheritance from `~/.config/codexa/`; emits provenance hashes used by PM, GO, and analytics loops.

## Governance
- **Version Control:** Git (branch-per-experiment worktrees)
- **Traceability:** TRACABILITY.md links architecture ↔ requirements ↔ implementation
- **Build System:** spekkit build process
- **Operating Model:** Hybrid configuration hierarchy—`.codexa/` per project with optional `extends:` to `~/.config/codexa/`; CI guards enforce FR-42/FR-43 compliance.
