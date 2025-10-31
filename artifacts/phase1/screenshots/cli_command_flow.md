# CLI Command Flow Mockup

```text
$ dynaforge /status milestone
MS-01: In Review
Pending approvals: CH-001 (FR-10)
Next agent: Tester (blocked)

$ dynaforge /ack CH-001 "Received designer spec"
ACK logged. Implementer notified.

$ dynaforge /resolve concern C-012
Concern C-012 marked resolved. QA will verify in next cycle.
```

> Shows parity between CLI interactions and Discord stub.
