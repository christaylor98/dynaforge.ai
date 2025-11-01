# Tech Stack Overview

## Interfaces
- **Primary Interface:** Python CLI for operator-facing workflows
- **Messaging Client:** Python client wiring directly into the discord bot framework

## Backend
- **Language:** Python 3.12
- **Web Framework:** FastAPI
- **API Spec:** OpenAPI 3.1
- **ORM:** SQLAlchemy 2.0
- **Caching:** Redis
- **Database:** PostgreSQL 11 (primary)
- **Analytics:** DuckDB + Parquet
- **Messaging:** NATS
- **Service Orchestration:** systemd timers + rsync-based ingestion

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

## Governance
- **Version Control:** Git (branch-per-experiment worktrees)
- **Traceability:** TRACABILITY.md links architecture ↔ requirements ↔ implementation
- **Build System:** spekkit build process
