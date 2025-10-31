# Approval Flow CLI Mockup

```text
$ dynaforge /status approvals
Approvals Pending:
- CH-001 / FR-10 — Stage: Human Reviewer — Requested 2025-10-30 14:18 UTC

$ dynaforge /approve CH-001 "QA blockers cleared"
Approval recorded by @stakeholder.
PM has resumed orchestration.

$ dynaforge /status approvals
No pending approvals.
```

> Demonstrates the gating workflow once a reviewer takes action.
