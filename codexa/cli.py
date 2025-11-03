"""
Codexa command-line interface.

Currently implements the `codexa discover` command which drives the
discovery workflow, computes blast-radius recommendations, and updates
history/audit artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

from scripts import discovery_bootstrap


def _render_text_summary(result: Dict[str, Any]) -> str:
    """Return a human-readable summary for text output."""
    lines = ["Discovery artifacts generated:"]
    for label, path in result["paths"].items():
        lines.append(f" - {label}: {path}")

    radius = result.get("blast_radius", {})
    changed_zones = radius.get("changed_zones") or []
    removed_zones = radius.get("removed_zones") or []
    recommended_agents = radius.get("recommended_agents") or []

    lines.append(
        f"Blast radius level: {radius.get('level', 'unknown')} "
        f"(zones: {', '.join(changed_zones) if changed_zones else 'none'})"
    )
    if removed_zones:
        lines.append(f"Zones removed: {', '.join(removed_zones)}")
    if recommended_agents:
        lines.append(f"Recommended agents: {', '.join(recommended_agents)}")
    notes = radius.get("notes") or []
    for note in notes:
        lines.append(f"- {note}")

    coverage = result.get("coverage", {})
    coverage_percent = coverage.get("coverage_percent")
    if coverage_percent is not None:
        lines.append(f"Coverage snapshot: {coverage_percent:.1f}%")

    return "\n".join(lines)


def discover_command(args: argparse.Namespace) -> int:
    result = discovery_bootstrap.run_discovery(
        config_path=args.config,
        mode_override=args.mode,
        log_handoff=args.log_handoff,
        track_history=not args.no_history,
    )

    if args.output == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_render_text_summary(result))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codexa",
        description="Codexa CLI — orchestrate discovery and change workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover_parser = subparsers.add_parser(
        "discover",
        help="Run the discovery pipeline and compute blast radius.",
    )
    discover_parser.add_argument(
        "--config",
        default=discovery_bootstrap.CONFIG_DEFAULT,
        type=Path,
        help="Path to discovery configuration (default: docs/discovery/config.yaml).",
    )
    discover_parser.add_argument(
        "--mode",
        choices=["full", "quick", "code-only"],
        help="Override discovery mode for this run.",
    )
    discover_parser.add_argument(
        "--log-handoff",
        dest="log_handoff",
        action="store_true",
        help="Append a discovery handoff entry to the audit log.",
    )
    discover_parser.add_argument(
        "--no-log-handoff",
        dest="log_handoff",
        action="store_false",
        help="Disable discovery handoff logging for this run.",
    )
    discover_parser.set_defaults(log_handoff=None)
    discover_parser.add_argument(
        "--no-history",
        action="store_true",
        help="Do not write discovery history entries (read-only mode).",
    )
    discover_parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Select output format (default: text).",
    )
    discover_parser.set_defaults(func=discover_command)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)  # type: ignore[call-arg]


if __name__ == "__main__":
    raise SystemExit(main())
