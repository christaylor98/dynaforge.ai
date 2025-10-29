#!/usr/bin/env python3
"""Summarize audit logs for Phase 0 demo."""

from __future__ import annotations

import json
from pathlib import Path


AUDIT_ROOT = Path("audit")
HANDOFF_FILE = AUDIT_ROOT / "handoff.jsonl"
CONCERN_FILE = AUDIT_ROOT / "concerns.jsonl"
COMMAND_FILE = AUDIT_ROOT / "commands.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def summarize_entries(entries: list[dict], *, key: str) -> str:
    count = len(entries)
    summary = f"{key.title()} entries: {count}"
    if count:
        latest = entries[-1]
        timestamp = latest.get("timestamp", "unknown")
        summary += f" (latest at {timestamp})"
    return summary


def main() -> None:
    handoffs = read_jsonl(HANDOFF_FILE)
    concerns = read_jsonl(CONCERN_FILE)
    commands = read_jsonl(COMMAND_FILE)

    print("Audit Summary")
    print(summarize_entries(handoffs, key="handoff"))
    print(summarize_entries(concerns, key="concern"))
    print(summarize_entries(commands, key="command"))


if __name__ == "__main__":
    main()
