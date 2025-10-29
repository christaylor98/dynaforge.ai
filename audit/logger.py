# Audit logging primitives for Phase 0 execution.
#
# Schema overview:
# - Handoff entry:
#   {
#       "record_type": "handoff",
#       "schema_version": "0.1.0",
#       "timestamp": "2024-01-01T00:00:00.000Z",
#       "phase": "0",
#       "from_agent": "implementer",
#       "to_agent": "tester",
#       "summary": "Initial skeleton ready for QA intake.",
#       "artifacts": ["docs/PROJECT_OVERVIEW.md"],
#       "concerns": [],
#       "metadata": {"notes": "Sample entry"}
#   }
# - Concern entry:
#   {
#       "record_type": "concern",
#       "schema_version": "0.1.0",
#       "timestamp": "2024-01-01T00:00:00.000Z",
#       "phase": "0",
#       "raised_by": "tester",
#       "severity": "medium",
#       "message": "Missing log rotation plan.",
#       "resolution": null,
#       "metadata": {"ticket": "QA-101"}
#   }
# - Command entry:
#   {
#       "record_type": "command",
#       "schema_version": "0.1.0",
#       "timestamp": "2024-01-01T00:00:00.000Z",
#       "phase": "0",
#       "issued_by": "discord-mock",
#       "command": "/status",
#       "arguments": [],
#       "metadata": {"notes": "Sample command log"}
#   }
#
# Consumers should treat these structures as append-only JSON Lines documents.

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Optional, Sequence

__all__ = ["AuditLogger", "log_handoff", "log_concern", "log_command"]

_ALLOWED_SEVERITIES = {"low", "medium", "high", "critical"}


def _utc_now() -> str:
    """Return an ISO-8601 timestamp in UTC with millisecond precision."""
    dt = datetime.now(timezone.utc)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _prepare_sequence(values: Optional[Sequence[str]]) -> list[str]:
    if not values:
        return []
    return [str(item) for item in values]


def _prepare_metadata(metadata: Optional[Mapping[str, Any]]) -> MutableMapping[str, Any]:
    if not metadata:
        return {}
    # Convert to a mutable dict to avoid leaking caller references.
    return dict(metadata)


@dataclass
class HandoffPayload:
    """Structured payload for handoff entries."""

    phase: str
    from_agent: str
    to_agent: str
    summary: str
    artifacts: Sequence[str] = field(default_factory=tuple)
    concerns: Sequence[str] = field(default_factory=tuple)
    metadata: Optional[Mapping[str, Any]] = None

    def to_entry(self, *, schema_version: str, timestamp: Optional[str] = None) -> MutableMapping[str, Any]:
        entry = {
            "record_type": "handoff",
            "schema_version": schema_version,
            "timestamp": timestamp or _utc_now(),
            "phase": str(self.phase),
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "summary": self.summary,
            "artifacts": _prepare_sequence(self.artifacts),
            "concerns": _prepare_sequence(self.concerns),
        }
        metadata = _prepare_metadata(self.metadata)
        if metadata:
            entry["metadata"] = metadata
        return entry


@dataclass
class ConcernPayload:
    """Structured payload for concern entries."""

    phase: str
    raised_by: str
    severity: str
    message: str
    resolution: Optional[str] = None
    metadata: Optional[Mapping[str, Any]] = None

    def to_entry(self, *, schema_version: str, timestamp: Optional[str] = None) -> MutableMapping[str, Any]:
        severity = self.severity.lower()
        if severity not in _ALLOWED_SEVERITIES:
            raise ValueError(f"Unsupported severity '{self.severity}'. Expected one of {_ALLOWED_SEVERITIES}.")

        entry = {
            "record_type": "concern",
            "schema_version": schema_version,
            "timestamp": timestamp or _utc_now(),
            "phase": str(self.phase),
            "raised_by": self.raised_by,
            "severity": severity,
            "message": self.message,
        }
        if self.resolution is not None:
            entry["resolution"] = self.resolution
        metadata = _prepare_metadata(self.metadata)
        if metadata:
            entry["metadata"] = metadata
        return entry


@dataclass
class CommandPayload:
    """Structured payload for interaction command entries."""

    phase: str
    issued_by: str
    command: str
    arguments: Sequence[str] = field(default_factory=tuple)
    metadata: Optional[Mapping[str, Any]] = None

    def to_entry(self, *, schema_version: str, timestamp: Optional[str] = None) -> MutableMapping[str, Any]:
        entry = {
            "record_type": "command",
            "schema_version": schema_version,
            "timestamp": timestamp or _utc_now(),
            "phase": str(self.phase),
            "issued_by": self.issued_by,
            "command": self.command,
            "arguments": _prepare_sequence(self.arguments),
        }
        metadata = _prepare_metadata(self.metadata)
        if metadata:
            entry["metadata"] = metadata
        return entry


class AuditLogger:
    """Append-only JSON Lines audit logger for handoff, concern, and command tracking."""

    def __init__(
        self,
        *,
        root: Path | str = Path("audit"),
        handoff_file: str = "handoff.jsonl",
        concern_file: str = "concerns.jsonl",
        command_file: str = "commands.jsonl",
        schema_version: str = "0.1.0",
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.handoff_path = self.root / handoff_file
        self.concern_path = self.root / concern_file
        self.command_path = self.root / command_file
        self.schema_version = schema_version

    def _append(self, path: Path, entry: Mapping[str, Any]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            json.dump(entry, handle, sort_keys=True)
            handle.write("\n")
        return path

    def log_handoff(
        self,
        *,
        phase: str,
        from_agent: str,
        to_agent: str,
        summary: str,
        artifacts: Optional[Sequence[str]] = None,
        concerns: Optional[Sequence[str]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> MutableMapping[str, Any]:
        payload = HandoffPayload(
            phase=phase,
            from_agent=from_agent,
            to_agent=to_agent,
            summary=summary,
            artifacts=artifacts or (),
            concerns=concerns or (),
            metadata=metadata,
        )
        entry = payload.to_entry(schema_version=self.schema_version, timestamp=timestamp)
        self._append(self.handoff_path, entry)
        return entry

    def log_concern(
        self,
        *,
        phase: str,
        raised_by: str,
        severity: str,
        message: str,
        resolution: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> MutableMapping[str, Any]:
        payload = ConcernPayload(
            phase=phase,
            raised_by=raised_by,
            severity=severity,
            message=message,
            resolution=resolution,
            metadata=metadata,
        )
        entry = payload.to_entry(schema_version=self.schema_version, timestamp=timestamp)
        self._append(self.concern_path, entry)
        return entry

    def log_command(
        self,
        *,
        phase: str,
        issued_by: str,
        command: str,
        arguments: Optional[Sequence[str]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> MutableMapping[str, Any]:
        payload = CommandPayload(
            phase=phase,
            issued_by=issued_by,
            command=command,
            arguments=arguments or (),
            metadata=metadata,
        )
        entry = payload.to_entry(schema_version=self.schema_version, timestamp=timestamp)
        self._append(self.command_path, entry)
        return entry


_DEFAULT_LOGGER = AuditLogger()


def log_handoff(**kwargs: Any) -> MutableMapping[str, Any]:
    """Convenience wrapper around the default logger."""
    return _DEFAULT_LOGGER.log_handoff(**kwargs)


def log_concern(**kwargs: Any) -> MutableMapping[str, Any]:
    """Convenience wrapper around the default logger."""
    return _DEFAULT_LOGGER.log_concern(**kwargs)


def log_command(**kwargs: Any) -> MutableMapping[str, Any]:
    """Convenience wrapper around the default logger."""
    return _DEFAULT_LOGGER.log_command(**kwargs)
