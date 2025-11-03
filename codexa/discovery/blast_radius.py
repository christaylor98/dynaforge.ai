"""
Blast radius planning for Codexa discovery runs.

The planner compares discovery outputs from consecutive runs and determines
which parts of the repository need to be refreshed.  Results are used to
decide which agents should execute and how much recomputation is necessary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


def _stable_hash(data: Any) -> str:
    """Return a deterministic SHA-256 hash for the provided data structure."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DiscoveryRunRecord:
    """Normalised data captured from a discovery run."""

    generated_at: str
    artifacts: Dict[str, str]
    zones: Dict[str, str]
    coverage_percent: float
    followups_open: Sequence[str] = field(default_factory=tuple)

    @classmethod
    def from_metrics(cls, payload: Mapping[str, Any]) -> "DiscoveryRunRecord":
        """Build a record from the metrics YAML payload."""
        metadata = payload.get("metadata", {})
        coverage = payload.get("coverage", {})
        artifacts_section = payload.get("artifacts", {})
        inputs_section = payload.get("inputs", {})

        artifacts: Dict[str, str] = {}
        for key, artifact in artifacts_section.items():
            digest = artifact.get("sha256")
            if digest:
                artifacts[key] = digest

        zones_payload: Iterable[Mapping[str, Any]] = payload.get("zones", []) or []
        zones = {
            str(entry.get("zone")): _stable_hash(entry)
            for entry in zones_payload
            if entry.get("zone") is not None
        }

        followups = tuple(inputs_section.get("followups_open") or [])

        return cls(
            generated_at=str(metadata.get("generated_at") or ""),
            artifacts=artifacts,
            zones=zones,
            coverage_percent=float(coverage.get("coverage_percent") or 0.0),
            followups_open=followups,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the record to a dict suitable for YAML/JSON storage."""
        return {
            "generated_at": self.generated_at,
            "artifacts": dict(self.artifacts),
            "zones": dict(self.zones),
            "coverage_percent": self.coverage_percent,
            "followups_open": list(self.followups_open),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "DiscoveryRunRecord":
        """Create a record from a previously serialised payload."""
        return cls(
            generated_at=str(payload.get("generated_at") or ""),
            artifacts=dict(payload.get("artifacts") or {}),
            zones=dict(payload.get("zones") or {}),
            coverage_percent=float(payload.get("coverage_percent") or 0.0),
            followups_open=tuple(payload.get("followups_open") or ()),
        )


@dataclass
class BlastRadiusResult:
    """Summary of differences between two discovery runs."""

    level: str
    changed_artifacts: List[str]
    changed_zones: List[str]
    removed_zones: List[str]
    coverage_delta: float
    followups_open: Sequence[str]
    recommended_agents: List[str]
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "changed_artifacts": self.changed_artifacts,
            "changed_zones": self.changed_zones,
            "removed_zones": self.removed_zones,
            "coverage_delta": self.coverage_delta,
            "followups_open": list(self.followups_open),
            "recommended_agents": self.recommended_agents,
            "notes": self.notes,
        }


class BlastRadiusPlanner:
    """Compute blast-radius recommendations between discovery runs."""

    AGENT_MATRIX: Dict[str, List[str]] = {
        "none": [],
        "local": ["discovery_analyzer"],
        "subsystem": [
            "discovery_analyzer",
            "requirements_intelligence",
            "system_model_builder",
        ],
        "system": [
            "discovery_analyzer",
            "requirements_intelligence",
            "system_model_builder",
            "project_manager",
        ],
    }

    def plan(
        self,
        current: DiscoveryRunRecord,
        previous: Optional[DiscoveryRunRecord],
    ) -> BlastRadiusResult:
        """Return blast-radius recommendation for the current run."""
        if previous is None:
            level = "system"
            notes = ["No previous run recorded; defaulting to full system recomputation."]
            return BlastRadiusResult(
                level=level,
                changed_artifacts=sorted(current.artifacts.keys()),
                changed_zones=sorted(current.zones.keys()),
                removed_zones=[],
                coverage_delta=current.coverage_percent,
                followups_open=current.followups_open,
                recommended_agents=self.AGENT_MATRIX[level],
                notes=notes,
            )

        changed_artifacts = self._diff_artifacts(current.artifacts, previous.artifacts)
        changed_zones, removed_zones = self._diff_zones(current.zones, previous.zones)

        coverage_delta = round(
            current.coverage_percent - previous.coverage_percent, 2
        )

        level = self._determine_level(
            changed_zones, current.zones.keys(), coverage_delta
        )

        notes = self._build_notes(
            changed_artifacts, changed_zones, removed_zones, coverage_delta
        )

        return BlastRadiusResult(
            level=level,
            changed_artifacts=changed_artifacts,
            changed_zones=changed_zones,
            removed_zones=removed_zones,
            coverage_delta=coverage_delta,
            followups_open=current.followups_open,
            recommended_agents=self.AGENT_MATRIX[level],
            notes=notes,
        )

    @staticmethod
    def _diff_artifacts(
        current: Mapping[str, str], previous: Mapping[str, str]
    ) -> List[str]:
        changed = [
            artifact
            for artifact, digest in current.items()
            if previous.get(artifact) != digest
        ]
        removed = [artifact for artifact in previous.keys() if artifact not in current]
        return sorted(set(changed + removed))

    @staticmethod
    def _diff_zones(
        current: Mapping[str, str], previous: Mapping[str, str]
    ) -> tuple[List[str], List[str]]:
        changed = [
            zone for zone, digest in current.items() if previous.get(zone) != digest
        ]
        removed = [zone for zone in previous.keys() if zone not in current]
        return sorted(changed), sorted(removed)

    def _determine_level(
        self,
        changed_zones: Sequence[str],
        all_zones: Iterable[str],
        coverage_delta: float,
    ) -> str:
        if not changed_zones and abs(coverage_delta) < 0.01:
            return "none"

        total_zones = max(len(list(all_zones)), 1)
        changed_count = len(changed_zones)
        ratio = changed_count / total_zones

        if changed_count <= 3 and ratio <= 0.2:
            level = "local"
        elif ratio <= 0.6:
            level = "subsystem"
        else:
            level = "system"

        if coverage_delta >= 10 and level != "system":
            level = "system"
        elif coverage_delta >= 5 and level == "local":
            level = "subsystem"

        return level

    @staticmethod
    def _build_notes(
        changed_artifacts: Sequence[str],
        changed_zones: Sequence[str],
        removed_zones: Sequence[str],
        coverage_delta: float,
    ) -> List[str]:
        notes = []
        if changed_artifacts:
            notes.append(
                f"Artifact digests changed for: {', '.join(changed_artifacts)}."
            )
        if changed_zones:
            notes.append(
                f"Zones impacted: {', '.join(changed_zones)}."
            )
        if removed_zones:
            notes.append(
                f"Zones removed since previous run: {', '.join(removed_zones)}."
            )
        if abs(coverage_delta) >= 0.01:
            direction = "increased" if coverage_delta >= 0 else "decreased"
            notes.append(f"Coverage {direction} by {abs(coverage_delta):.2f}%.")
        if not notes:
            notes.append("No material changes detected.")
        return notes
