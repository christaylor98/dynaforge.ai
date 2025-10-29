#!/usr/bin/env python3
"""QA policy parser stub for Phase 0.

The parser expects a JSON-compatible YAML document with the following structure:
{
  "policy": {
    "phase": "0",
    "coverage_threshold": 0.80,
    "reproducibility_threshold": 0.95,
    "gates": [
      {"id": "coverage", "metric": "coverage", "operator": ">=", "target": 0.8}
    ]
  },
  "notifications": {
    "on_failure": ["raise_concern"],
    "discord_channel": "#qa-alerts"
  }
}

Only a subset of YAML is supported; JSON syntax is valid.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

DEFAULT_POLICY_PATH = Path("QA_POLICY.yaml")


class PolicyValidationError(Exception):
    """Raised when the QA policy file is malformed."""


def load_policy(path: Path) -> Dict[str, Any]:
    """Load a policy file containing JSON-compatible YAML."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PolicyValidationError(f"Policy file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PolicyValidationError(f"Policy file is not valid JSON/YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise PolicyValidationError("Policy root must be a mapping/object.")
    return data


def validate_policy(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate required fields and return canonicalized policy."""
    if "policy" not in data or not isinstance(data["policy"], dict):
        raise PolicyValidationError("Missing 'policy' section.")
    if "notifications" not in data or not isinstance(data["notifications"], dict):
        raise PolicyValidationError("Missing 'notifications' section.")

    policy = data["policy"]
    notifications = data["notifications"]

    required_policy_fields = ("phase", "coverage_threshold", "reproducibility_threshold", "gates")
    for field in required_policy_fields:
        if field not in policy:
            raise PolicyValidationError(f"Policy section missing required field '{field}'.")

    if not isinstance(policy["gates"], list) or not policy["gates"]:
        raise PolicyValidationError("Policy 'gates' must be a non-empty list.")

    for index, gate in enumerate(policy["gates"], start=1):
        if not isinstance(gate, dict):
            raise PolicyValidationError(f"Gate #{index} is not an object.")
        for field in ("id", "metric", "operator", "target"):
            if field not in gate:
                raise PolicyValidationError(f"Gate #{index} missing '{field}'.")

    if "on_failure" not in notifications or not isinstance(notifications["on_failure"], list):
        raise PolicyValidationError("Notifications must include 'on_failure' list.")

    return {"policy": policy, "notifications": notifications}


def render_summary(policy: Dict[str, Any]) -> str:
    gates = policy["policy"]["gates"]
    gate_lines: List[str] = [f"- {gate['id']}: {gate['metric']} {gate['operator']} {gate['target']}" for gate in gates]
    gate_section = "\n".join(gate_lines)
    notifications = ", ".join(policy["notifications"]["on_failure"])
    return (
        f"QA Policy Summary\n"
        f"Phase: {policy['policy']['phase']}\n"
        f"Coverage Threshold: {policy['policy']['coverage_threshold']}\n"
        f"Reproducibility Threshold: {policy['policy']['reproducibility_threshold']}\n"
        f"Gates:\n{gate_section}\n"
        f"Notifications on failure: {notifications}"
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QA Policy Parser Stub")
    parser.add_argument(
        "policy_path",
        nargs="?",
        default=str(DEFAULT_POLICY_PATH),
        help="Path to QA policy file (JSON-compatible YAML).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    path = Path(args.policy_path)
    try:
        data = load_policy(path)
        validated = validate_policy(data)
    except PolicyValidationError as exc:
        print(f"Policy validation error: {exc}", file=sys.stderr)
        return 1

    summary = render_summary(validated)
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
