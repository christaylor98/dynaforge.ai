#!/usr/bin/env python3
"""Minimal QA enforcement CLI for Phase 1 runs.

Evaluates QA metrics against `QA_POLICY.yaml` and exits non-zero if a gate fails.
Outputs a JSON summary so Validate stage can record the result.
"""

from __future__ import annotations

import argparse
import json
import operator
import sys
from pathlib import Path
from typing import Any, Dict

from policy_parser import load_policy, validate_policy, PolicyValidationError

OPERATORS = {
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
    "==": operator.eq,
}


def load_metrics(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Metrics file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Metrics file is not valid JSON: {exc}") from exc


def load_results(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Results file invalid JSON: {exc}") from exc


def evaluate(policy: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
    gates = policy["policy"]["gates"]
    evaluation = {"passed": True, "gates": []}

    for gate in gates:
        metric_name = gate["metric"]
        metric_value = metrics.get(metric_name)
        op_symbol = gate["operator"]
        comparator = OPERATORS.get(op_symbol)
        if comparator is None:
            raise SystemExit(f"Unsupported operator '{op_symbol}' in policy gate '{gate['id']}'")
        if metric_value is None:
            gate_result = {
                "id": gate["id"],
                "metric": metric_name,
                "expected": gate,
                "actual": None,
                "status": "missing",
                "message": f"Metric '{metric_name}' not provided."
            }
            evaluation["passed"] = False
            evaluation["gates"].append(gate_result)
            continue

        passed = comparator(metric_value, gate["target"])
        gate_result = {
            "id": gate["id"],
            "metric": metric_name,
            "expected": gate,
            "actual": metric_value,
            "status": "pass" if passed else "fail",
            "message": "" if passed else f"Expected {metric_name} {op_symbol} {gate['target']} but got {metric_value}."
        }
        if not passed:
            evaluation["passed"] = False
        evaluation["gates"].append(gate_result)
    return evaluation


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce QA policy gates for a change run.")
    parser.add_argument("--policy", default="QA_POLICY.yaml", help="Path to QA policy file.")
    parser.add_argument("--metrics", required=True, help="Path to JSON metrics file (coverage, reproducibility, etc.)")
    parser.add_argument("--results", help="Optional path to tests results JSON for reference.")
    parser.add_argument("--change-id", required=True, help="Change identifier (e.g., CH-002).")
    parser.add_argument("--output", required=True, help="Path to write the enforcement summary JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Return 0 even if gates fail (for diagnostics).")

    args = parser.parse_args()

    policy_path = Path(args.policy)
    metrics_path = Path(args.metrics)
    output_path = Path(args.output)

    try:
        policy_data = validate_policy(load_policy(policy_path))
    except PolicyValidationError as exc:
        print(f"Policy validation error: {exc}", file=sys.stderr)
        return 1

    metrics = load_metrics(metrics_path)
    results = load_results(Path(args.results)) if args.results else {}

    evaluation = evaluate(policy_data, metrics)
    evaluation["change_id"] = args.change_id
    evaluation["policy_path"] = str(policy_path)
    evaluation["metrics_path"] = str(metrics_path)
    evaluation["results_path"] = args.results
    evaluation["dry_run"] = args.dry_run

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evaluation, indent=2, sort_keys=True), encoding="utf-8")

    if evaluation["passed"]:
        print("QA enforcement passed.")
        return 0

    print("QA enforcement failed:")
    for gate in evaluation["gates"]:
        if gate["status"] != "pass":
            print(f" - {gate['id']}: {gate['message']}")
    return 0 if args.dry_run else 2


if __name__ == "__main__":
    raise SystemExit(main())
