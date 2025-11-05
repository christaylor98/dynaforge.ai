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
from . import config_tools


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
    project_root = Path(args.project).expanduser().resolve() if args.project else Path.cwd()
    result = discovery_bootstrap.run_discovery(
        config_path=args.config,
        mode_override=args.mode,
        log_handoff=args.log_handoff,
        track_history=not args.no_history,
        project_root=project_root,
    )

    if args.output == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_render_text_summary(result))
    return 0


def init_command(args: argparse.Namespace) -> int:
    if not args.operating_model:
        raise SystemExit(
            "codexa init currently supports only --operating-model scaffolding."
        )

    root = (args.root or Path.cwd()).expanduser().resolve() / ".codexa"
    report = config_tools.scaffold_operating_model(root, force=args.force)
    print(
        f"Operating model scaffold created at {report['root']} "
        f"(directories: {len(report['directories'])}, files: {len(report['files'])})"
    )
    for warning in report.get("warnings", []):
        print(f"[WARN] {warning}")
    return 0


def doctor_command(args: argparse.Namespace) -> int:
    report = config_tools.inspect_configuration(
        config_root=args.config_root,
        start_path=args.start_path,
    )
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(config_tools.render_doctor_text(report))

    if not args.no_telemetry:
        config_tools.append_doctor_audit(report)
    return int(report.get("exit_code", 0))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codexa",
        description="Codexa CLI — orchestrate discovery and change workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init",
        help="Initialise Codexa assets (operating model scaffolding, etc.).",
    )
    init_parser.add_argument(
        "--root",
        type=Path,
        help="Project root where `.codexa/` should be created (defaults to CWD).",
    )
    init_parser.add_argument(
        "--operating-model",
        action="store_true",
        help="Scaffold the `.codexa/` operating model directory.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing scaffold files.",
    )
    init_parser.set_defaults(func=init_command)

    discover_parser = subparsers.add_parser(
        "discover",
        help="Run the discovery pipeline and compute blast radius.",
    )
    discover_parser.add_argument(
        "--config",
        type=Path,
        help="Path to discovery configuration (defaults to project `.codexa` config).",
    )
    discover_parser.add_argument(
        "--project",
        type=Path,
        help="Project root to analyse (defaults to current working directory).",
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

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Validate Codexa configuration and report provenance.",
    )
    sub_doctor = doctor_parser.add_subparsers(dest="doctor_command", required=True)

    doctor_config_parser = sub_doctor.add_parser(
        "config",
        help="Inspect `.codexa/` scaffolding, global bundles, and provenance hashes.",
    )
    doctor_config_parser.add_argument(
        "--config-root",
        type=Path,
        help="Explicit path to `.codexa/` directory (defaults to auto-discovery).",
    )
    doctor_config_parser.add_argument(
        "--start-path",
        type=Path,
        help="Starting directory for discovery when --config-root is not provided.",
    )
    doctor_config_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    doctor_config_parser.add_argument(
        "--no-telemetry",
        action="store_true",
        help="Do not append the report to audit/doctor_config.jsonl.",
    )
    doctor_config_parser.set_defaults(func=doctor_command)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)  # type: ignore[call-arg]


if __name__ == "__main__":
    raise SystemExit(main())
