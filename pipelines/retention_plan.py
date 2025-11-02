#!/usr/bin/env python3
"""Create retention plan summary for a change workspace."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List


def list_runs(path: Path) -> List[str]:
    if not path.exists():
        return []
    return sorted(str(p) for p in path.iterdir() if p.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description="Build retention plan for change runs.")
    parser.add_argument("change_id", help="Change identifier (e.g., CH-002)")
    parser.add_argument("--runs-path", default="artifacts/work", help="Root path containing change runs")
    parser.add_argument("--output", required=True, help="Path to output retention plan JSON")
    args = parser.parse_args()

    runs_root = Path(args.runs_path) / args.change_id
    runs = list_runs(runs_root)
    plan = {
        "change_id": args.change_id,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "runs": runs,
        "policy": {
            "auto_purge_after_hours": 48,
            "max_storage_gb": 2,
        },
        "retain_flags": [str(p) for p in runs_root.glob("**/.retain")],
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
