# CLI Command Flow Mockup

```text
$ codexa status --section discovery
discovery: complete (mode=full)
followups: issue-12 (needs approval)
coverage: 68%

$ codexa prompt "approve design for CH-010"
AI: Confirming — design for CH-010 approved.

$ codexa prompt "assign gap-03 to impact assessor"
AI: Recorded. gap-03 owner → IA.

$ codexa prompt "publish governance report"
AI: Gaps remain (gap-02). Publish anyway?
Human: "schedule follow-up tomorrow"
AI: Follow-up logged. Governance report deferred.
```

> Updated to illustrate the prompt-first interaction model with optional CLI aliasing.
