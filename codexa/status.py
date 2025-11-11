"""
Status and recommendation helpers for the Codexa CLI.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class DiscoverySnapshot:
    timestamp: Optional[_dt.datetime]
    coverage: Optional[float]
    blast_level: Optional[str]
    followups_open: List[str]


def _pick_config(project_root: Path) -> Optional[Path]:
    candidates = [
        project_root / ".codexa" / "config.yaml",
        project_root / "docs" / "discovery" / "config.yaml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _parse_iso(timestamp: Optional[str]) -> Optional[_dt.datetime]:
    if not timestamp:
        return None
    value = timestamp.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return _dt.datetime.fromisoformat(value)
    except ValueError:
        return None


def _load_history(project_root: Path) -> DiscoverySnapshot:
    history_path = project_root / "analysis" / "history" / "discovery_runs.yaml"
    if not history_path.exists():
        return DiscoverySnapshot(None, None, None, [])

    try:
        data = yaml.safe_load(history_path.read_text(encoding="utf-8")) or []
    except yaml.YAMLError:
        return DiscoverySnapshot(None, None, None, [])

    if not isinstance(data, list) or not data:
        return DiscoverySnapshot(None, None, None, [])

    last_entry = data[-1]
    if not isinstance(last_entry, dict):
        return DiscoverySnapshot(None, None, None, [])

    record = last_entry.get("record", {})
    blast = last_entry.get("blast_radius", {})

    timestamp = _parse_iso(record.get("generated_at"))
    coverage = None
    try:
        coverage_value = record.get("coverage_percent")
        coverage = float(coverage_value) if coverage_value is not None else None
    except (TypeError, ValueError):
        coverage = None

    blast_level = blast.get("level") if isinstance(blast, dict) else None
    followups = record.get("followups_open") or blast.get("followups_open") or []
    followup_list = [item for item in followups if isinstance(item, str)]

    return DiscoverySnapshot(timestamp, coverage, blast_level, followup_list)


def _format_timedelta(delta: _dt.timedelta) -> str:
    total_seconds = int(abs(delta.total_seconds()))
    if total_seconds < 60:
        return "just now"
    minutes, _ = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    parts: List[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes and not days:
        parts.append(f"{minutes}m")
    descriptor = " ".join(parts)
    return f"{descriptor} ago"


def gather_status(project_root: Path) -> Dict[str, Any]:
    project_root = project_root.expanduser().resolve()
    config_path = _pick_config(project_root)
    snapshot = _load_history(project_root)

    now = _dt.datetime.now(tz=_dt.timezone.utc)
    last_run_age = None
    if snapshot.timestamp:
        if snapshot.timestamp.tzinfo is None:
            snapshot_ts = snapshot.timestamp.replace(tzinfo=_dt.timezone.utc)
        else:
            snapshot_ts = snapshot.timestamp.astimezone(_dt.timezone.utc)
        last_run_age = now - snapshot_ts

    recommendation = "Run an initial discovery scan."
    suggested_command = f"codexa discover --project {project_root}"

    if not config_path:
        recommendation = "Bootstrap discovery config and run the first scan."
        suggested_command = "codexa discover"
    elif snapshot.timestamp is None:
        recommendation = "Run the first discovery scan."
        suggested_command = "codexa discover"
    elif last_run_age and last_run_age > _dt.timedelta(hours=24):
        recommendation = "Discovery snapshot is over 24 hours old; refresh it."
        suggested_command = "codexa discover"
    elif snapshot.followups_open:
        recommendation = (
            "Resolve open follow-ups from the last discovery run before proceeding."
        )
        suggested_command = None
    else:
        recommendation = "Discovery looks fresh. Consider a quick follow-up run if needed."
        suggested_command = "codexa discover"

    summary = {
        "project_root": str(project_root),
        "config_path": str(config_path) if config_path else None,
        "config_present": config_path is not None,
        "last_run_timestamp": snapshot.timestamp.isoformat()
        if snapshot.timestamp
        else None,
        "last_run_age": last_run_age,
        "coverage": snapshot.coverage,
        "blast_level": snapshot.blast_level,
        "followups_open": snapshot.followups_open,
        "recommendation": recommendation,
        "suggested_command": suggested_command,
    }
    return summary


def render_status_text(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"Project: {report.get('project_root')}")

    if report.get("config_present"):
        lines.append(f"Config: {report.get('config_path')}")
    else:
        lines.append("Config: not found (will be bootstrapped on next discovery run)")

    timestamp = report.get("last_run_timestamp")
    last_run_line = "Last discovery: never"
    if timestamp:
        age = report.get("last_run_age")
        if isinstance(age, _dt.timedelta):
            last_run_line = f"Last discovery: {timestamp} ({_format_timedelta(age)})"
        else:
            last_run_line = f"Last discovery: {timestamp}"
    lines.append(last_run_line)

    coverage = report.get("coverage")
    if isinstance(coverage, (int, float)):
        lines.append(f"Coverage: {coverage:.1f}%")

    blast_level = report.get("blast_level")
    if blast_level:
        lines.append(f"Blast radius: {blast_level}")

    followups = report.get("followups_open") or []
    lines.append(f"Open follow-ups: {len(followups)}")
    if followups:
        lines.append("  - " + ", ".join(followups))

    lines.append(f"Recommendation: {report.get('recommendation')}")
    suggested = report.get("suggested_command")
    if suggested:
        lines.append(f"Suggested command: {suggested}")

    return "\n".join(lines)
