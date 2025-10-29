#!/usr/bin/env python3
"""Utilities for managing concern lifecycle and syncing summaries into docs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable, List, MutableMapping, Optional

if __package__ is None or __package__ == "":
    # Allow running as a script.
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))

from audit import AuditLogger

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_ROOT = PROJECT_ROOT / "audit"
DEFAULT_PROJECT_DETAIL = PROJECT_ROOT / "docs" / "PROJECT_DETAIL.md"

CONCERNS_START = "<!-- concerns:start -->"
CONCERNS_END = "<!-- concerns:end -->"
_CONCERN_SECTION_PATTERN = re.compile(
    rf"{CONCERNS_START}.*?{CONCERNS_END}", re.DOTALL | re.MULTILINE
)

_SEVERITY_CHOICES = ("low", "medium", "high", "critical")


def _utc_now() -> str:
    """Return timestamp consistent with audit logger formatting."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _ensure_path(path: Path) -> Path:
    return Path(path).expanduser().resolve()


def _load_entries(concerns_path: Path) -> list[MutableMapping[str, Any]]:
    if not concerns_path.exists():
        return []
    entries: list[MutableMapping[str, Any]] = []
    with concerns_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            entry = json.loads(line)
            entries.append(entry)
    return entries


def _write_entries(concerns_path: Path, entries: Iterable[MutableMapping[str, Any]]) -> None:
    concerns_path.parent.mkdir(parents=True, exist_ok=True)
    with concerns_path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            json.dump(entry, handle, sort_keys=True)
            handle.write("\n")


def load_concerns(*, audit_root: Path = DEFAULT_AUDIT_ROOT) -> list[MutableMapping[str, Any]]:
    """Return concern entries from the audit store."""
    concerns_path = _ensure_path(audit_root) / "concerns.jsonl"
    return [
        entry
        for entry in _load_entries(concerns_path)
        if entry.get("record_type") == "concern"
    ]


def raise_concern(
    *,
    phase: str,
    raised_by: str,
    severity: str,
    message: str,
    concern_id: str | None = None,
    metadata: Optional[MutableMapping[str, Any]] = None,
    audit_root: Path = DEFAULT_AUDIT_ROOT,
) -> MutableMapping[str, Any]:
    """Append a new concern to the audit log and return the entry."""
    logger = AuditLogger(root=_ensure_path(audit_root))
    entry = logger.log_concern(
        phase=phase,
        raised_by=raised_by,
        severity=severity,
        message=message,
        concern_id=concern_id,
        metadata=metadata,
    )
    return entry


def update_concern(
    concern_id: str,
    *,
    audit_root: Path = DEFAULT_AUDIT_ROOT,
    severity: str | None = None,
    message: str | None = None,
    note: str | None = None,
) -> MutableMapping[str, Any]:
    """Update an existing concern entry."""
    concerns_path = _ensure_path(audit_root) / "concerns.jsonl"
    entries = _load_entries(concerns_path)

    target: MutableMapping[str, Any] | None = None
    for entry in entries:
        if entry.get("record_type") == "concern" and entry.get("concern_id") == concern_id:
            target = entry
            break

    if target is None:
        raise ValueError(f"Concern '{concern_id}' not found.")

    if severity:
        normalized = severity.lower()
        if normalized not in _SEVERITY_CHOICES:
            raise ValueError(f"Unsupported severity '{severity}'. Expected one of {_SEVERITY_CHOICES}.")
        target["severity"] = normalized
    if message:
        target["message"] = message
    if note:
        metadata = target.setdefault("metadata", {})
        notes = metadata.setdefault("notes", [])
        if not isinstance(notes, list):
            notes = metadata["notes"] = []
        notes.append({"timestamp": _utc_now(), "note": note})
    target.setdefault("metadata", {})["updated_timestamp"] = _utc_now()

    _write_entries(concerns_path, entries)
    return target


def resolve_concern(
    concern_id: str,
    *,
    resolution: str,
    audit_root: Path = DEFAULT_AUDIT_ROOT,
    note: str | None = None,
) -> MutableMapping[str, Any]:
    """Mark a concern as resolved with the provided resolution text."""
    entry = update_concern(concern_id, audit_root=audit_root, note=note)
    entry["resolution"] = resolution
    metadata = entry.setdefault("metadata", {})
    metadata["resolved_timestamp"] = _utc_now()

    concerns_path = _ensure_path(audit_root) / "concerns.jsonl"
    entries = _load_entries(concerns_path)
    for stored in entries:
        if stored.get("record_type") == "concern" and stored.get("concern_id") == concern_id:
            stored["resolution"] = entry["resolution"]
            stored.setdefault("metadata", {}).update(metadata)
    _write_entries(concerns_path, entries)
    return entry


def _escape_markdown(text: str) -> str:
    return text.replace("|", r"\|")


def _render_table(
    concerns: Iterable[MutableMapping[str, Any]],
    *,
    include_resolution: bool = False,
) -> list[str]:
    items: List[MutableMapping[str, Any]] = sorted(concerns, key=lambda item: item.get("timestamp", ""))
    if not items:
        return ["- None."]

    if include_resolution:
        header = "| ID | Severity | Message | Raised By | Raised At | Resolution | Resolved At |"
        separator = "| -- | -------- | ------- | --------- | --------- | ---------- | ----------- |"
    else:
        header = "| ID | Severity | Message | Raised By | Raised At |"
        separator = "| -- | -------- | ------- | --------- | --------- |"

    rows = [header, separator]
    for entry in items:
        concern_id = entry.get("concern_id", "n/a")
        severity = entry.get("severity", "n/a")
        message = _escape_markdown(entry.get("message", ""))
        raised_by = entry.get("raised_by", "n/a")
        timestamp = entry.get("timestamp", "n/a")
        if include_resolution:
            resolution = _escape_markdown(entry.get("resolution", "n/a"))
            resolved_at = entry.get("metadata", {}).get("resolved_timestamp", "n/a")
            row = f"| {concern_id} | {severity} | {message} | {raised_by} | {timestamp} | {resolution} | {resolved_at} |"
        else:
            row = f"| {concern_id} | {severity} | {message} | {raised_by} | {timestamp} |"
        rows.append(row)
    return rows


def _render_concern_section(
    concerns: Iterable[MutableMapping[str, Any]],
) -> str:
    open_concerns = [entry for entry in concerns if not entry.get("resolution")]
    resolved_concerns = [entry for entry in concerns if entry.get("resolution")]

    lines: list[str] = [
        CONCERNS_START,
        "",
        "### Concern Summary",
        "",
        "#### Open Concerns",
        "",
        * _render_table(open_concerns),
        "",
        "#### Resolved Concerns",
        "",
        * _render_table(resolved_concerns, include_resolution=True),
        "",
        CONCERNS_END,
    ]
    return "\n".join(lines)


def sync_concerns(
    *,
    audit_root: Path = DEFAULT_AUDIT_ROOT,
    project_detail_path: Path = DEFAULT_PROJECT_DETAIL,
) -> str:
    """Refresh the concern section within PROJECT_DETAIL.md."""
    concerns = load_concerns(audit_root=audit_root)
    section = _render_concern_section(concerns)

    project_detail_path = _ensure_path(project_detail_path)
    project_detail_path.parent.mkdir(parents=True, exist_ok=True)
    content = ""
    if project_detail_path.exists():
        content = project_detail_path.read_text(encoding="utf-8")

    if _CONCERN_SECTION_PATTERN.search(content):
        updated = _CONCERN_SECTION_PATTERN.sub(section, content)
    else:
        prefix = content.rstrip()
        if prefix:
            prefix += "\n\n"
        updated = prefix + section + "\n"
    if not updated.endswith("\n"):
        updated += "\n"

    project_detail_path.write_text(updated, encoding="utf-8")
    return section


def _add_raise_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("raise", help="Raise a new concern.")
    parser.add_argument("--phase", default="1", help="Phase identifier for the concern.")
    parser.add_argument("--raised-by", default="tester", help="Agent raising the concern.")
    parser.add_argument(
        "--severity",
        required=True,
        choices=_SEVERITY_CHOICES,
        help="Severity level for the concern.",
    )
    parser.add_argument("--message", required=True, help="Concern message.")
    parser.add_argument("--concern-id", help="Optional explicit concern identifier.")
    parser.add_argument("--note", help="Optional note recorded in metadata.")
    parser.add_argument("--audit-root", default=str(DEFAULT_AUDIT_ROOT), help="Path to audit directory.")


def _add_update_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("update", help="Update an existing concern.")
    parser.add_argument("concern_id", help="Identifier of the concern to update.")
    parser.add_argument("--severity", choices=_SEVERITY_CHOICES, help="New severity level.")
    parser.add_argument("--message", help="Updated concern message.")
    parser.add_argument("--note", help="Note to append to concern metadata.")
    parser.add_argument("--audit-root", default=str(DEFAULT_AUDIT_ROOT), help="Path to audit directory.")


def _add_resolve_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("resolve", help="Resolve an existing concern.")
    parser.add_argument("concern_id", help="Identifier of the concern to resolve.")
    parser.add_argument("--resolution", required=True, help="Resolution description.")
    parser.add_argument("--note", help="Optional note to append to metadata.")
    parser.add_argument("--audit-root", default=str(DEFAULT_AUDIT_ROOT), help="Path to audit directory.")


def _add_sync_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("sync", help="Sync concerns into project detail documentation.")
    parser.add_argument("--audit-root", default=str(DEFAULT_AUDIT_ROOT), help="Path to audit directory.")
    parser.add_argument(
        "--project-detail",
        default=str(DEFAULT_PROJECT_DETAIL),
        help="Path to PROJECT_DETAIL.md.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Concern lifecycle management utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_raise_parser(subparsers)
    _add_update_parser(subparsers)
    _add_resolve_parser(subparsers)
    _add_sync_parser(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "raise":
        entry = raise_concern(
            phase=args.phase,
            raised_by=args.raised_by,
            severity=args.severity,
            message=args.message,
            concern_id=args.concern_id,
            metadata={"notes": [{"timestamp": _utc_now(), "note": args.note}]} if args.note else None,
            audit_root=Path(args.audit_root),
        )
        print(json.dumps(entry, indent=2, sort_keys=True))
        return 0

    if args.command == "update":
        entry = update_concern(
            args.concern_id,
            audit_root=Path(args.audit_root),
            severity=args.severity,
            message=args.message,
            note=args.note,
        )
        print(json.dumps(entry, indent=2, sort_keys=True))
        return 0

    if args.command == "resolve":
        entry = resolve_concern(
            args.concern_id,
            resolution=args.resolution,
            audit_root=Path(args.audit_root),
            note=args.note,
        )
        print(json.dumps(entry, indent=2, sort_keys=True))
        return 0

    if args.command == "sync":
        section = sync_concerns(
            audit_root=Path(args.audit_root),
            project_detail_path=Path(args.project_detail),
        )
        print(section)
        return 0

    parser.error("Unknown command.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
