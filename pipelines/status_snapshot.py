#!/usr/bin/env python3
"""Generate status snapshot JSON for a change workspace."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

TABLE_PATTERN = re.compile(r"\|\s*(?P<stage>[A-Za-z ]+)\s*\|\s*(?P<reviewer>[^|]+)\|\s*(?P<status>[^|]+)\|\s*(?P<notes>[^|]+)\|")


def parse_status(md_path: Path) -> dict:
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    table_started = False
    entries = []
    for line in lines:
        if line.strip().startswith("| Stage"):
            table_started = True
            continue
        if table_started:
            if not line.strip() or line.strip().startswith("##"):
                break
            match = TABLE_PATTERN.match(line)
            if match:
                entries.append({
                    "stage": match.group("stage").strip(),
                    "reviewer": match.group("reviewer").strip(),
                    "status": match.group("status").strip(),
                    "notes": match.group("notes").strip(),
                })
    return {
        "change_id": md_path.parent.name,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate status snapshot for CH workspace.")
    parser.add_argument("workspace", help="Path to change status Markdown file (e.g., changes/CH-002/status.md)")
    parser.add_argument("--output", required=True, help="Path to output snapshot JSON.")
    args = parser.parse_args()

    md_path = Path(args.workspace)
    if not md_path.exists():
        parser.error(f"Status file not found: {md_path}")

    snapshot = parse_status(md_path)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(snapshot, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
