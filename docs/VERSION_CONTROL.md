# 🧭 Version Control Strategy

This document defines how Git is used across the project to ensure **traceability**, **governed evolution**, and **high-velocity experimentation**.

---

## 1. Core Principles

| Principle | Description |
|------------|--------------|
| **Traceable evolution** | Every change to architecture, requirements, or implementation must link back to a branch, PR, and version tag. |
| **Human-in-the-loop checkpoints** | Merges to `main` occur only after an explicit checkpoint review verifying documentation, traceability, and tests are up to date. |
| **Experiment freedom** | Agents and developers can spin off isolated experiments via `git worktree` without cluttering history. |
| **Governed artifacts** | When a document or feature has been incorporated, it is **clipped** (prepend `_c_`) to mark completion. |
| **Automation friendly** | The structure supports both human and agent workflows through consistent naming and tagging conventions. |

---

## 2. Branching Model

| Branch | Purpose | Merge Direction |
|---------|----------|----------------|
| **`main`** | Source of truth for stable, governed releases. Each merge here corresponds to a reviewed version tag. | ← `develop` |
| **`develop`** | Integration branch for active, non-experimental work. | ↔ `feature/*` / `experiment/*` |
| **`feature/*`** | Short-lived branches for specific features, docs, or fixes. | → `develop` |
| **`experiment/*`** | Worktree branches for research, prototypes, or agent experiments. | optional → `develop` |
| **`hotfix/*`** | Emergency patches for production. | → `main` + `develop` |

---

## 3. Worktree Workflow

### Create and use an experiment worktree

```bash
# Create a detached worktree for isolated work
git worktree add ../overlord-exp1 experiment/agent-loop
cd ../overlord-exp1

# Commit as normal
git add .
git commit -m "feat(exp): first agent loop prototype"
````

When finished:

```bash
cd ../main-repo
git worktree remove ../overlord-exp1
```

### Merge flow

1. Rebase experiment on `develop`.
2. Merge non-conflicting improvements.
3. Retain experimental logic in the archived branch (`exp-<name>` tag).
4. Clip documents that were successfully integrated.

---

## 4. Commit & Tag Conventions

### Commit Format

```
<type>(<scope>): <summary>

[optional body]
```

**Common types**

* `feat`: new functionality
* `fix`: bug fix
* `docs`: documentation updates
* `test`: testing changes
* `refactor`: structural improvements
* `spec`: architecture/requirements/test alignment updates
* `chore`: maintenance, formatting, or tooling

### Examples

```
feat(core): add async data loader
spec(architecture): update data pipeline diagram
fix(parser): handle empty response from broker API
```

### Tagging

| Tag                   | Description                              |
| --------------------- | ---------------------------------------- |
| `vX.Y.Z`              | Stable version, aligned with docs/tests. |
| `checkpoint-YYYYMMDD` | Marks a human-reviewed milestone.        |
| `exp-<name>`          | Snapshot of an experiment or prototype.  |

---

## 5. Review & Merge Process

1. **Developer/Agent completes branch** and opens a PR → `develop`.
2. **Automated checks** run:

   * Lint & tests
   * `TRACABILITY.md` consistency
   * Doc/spec alignment (`/speckit.check` equivalent)
3. **Human checkpoint** (if required) reviews architecture, requirements, and test coverage.
4. Merge → `develop`.
5. When milestone is met, merge `develop` → `main` with a release tag.

---

## 6. Versioning Rules

| Change Type | Increment Example | Trigger                               |
| ----------- | ----------------- | ------------------------------------- |
| **Patch**   | `1.0.1`           | Bug fix, non-breaking improvement     |
| **Minor**   | `1.1.0`           | New feature, backward compatible      |
| **Major**   | `2.0.0`           | Breaking architectural or API changes |

Each merge to `main` must:

* Tag with `vX.Y.Z`
* Update `CHANGELOG.md`
* Optionally trigger clipping of completed docs

---

## 7. Integration With Agents

| Layer                     | Purpose                                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Codex MCP / AI Agents** | Operate within isolated branches or worktrees using sandbox write access.                              |
| **Automated Commits**     | Use `[agent:<role>]` in commit metadata for traceability.                                              |
| **Agent Governance**      | Only the *Project Manager agent* merges to `develop`; human approval is required for merges to `main`. |

Example:

```
feat(simulation): add regime clustering module [agent:Backend]
```

---

## 8. Example CLI Reference

```bash
# Initialize repository
git init
git checkout -b develop

# Start new feature
git checkout -b feature/trade-evaluator

# Merge feature
git checkout develop
git merge --no-ff feature/trade-evaluator
git branch -d feature/trade-evaluator

# Prepare release
git checkout main
git merge --no-ff develop
git tag -a v1.0.0 -m "Initial governed release"
git push origin main --tags
```

---

## 9. Governance Checklist

Before merging to `main`:

* [ ] `TRACABILITY.md` updated
* [ ] Requirements and architecture synced
* [ ] Tests verified and results attached
* [ ] CHANGELOG.md updated
* [ ] Version tag created
* [ ] `_c_` prefix applied to completed docs

---

**Document last updated:** `2025-11-02 (CH-001 Phase 0 refresh)`

---
