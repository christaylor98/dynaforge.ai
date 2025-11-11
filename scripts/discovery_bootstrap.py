#!/usr/bin/env python3
"""
Bootstrap discovery artifacts for MS-02 Phase 0.

Reads `docs/discovery/config.yaml`, scans the repository, and generates:
  - analysis/system_manifest.yaml
  - analysis/change_zones.md
  - analysis/intent_map.md

This script is a stop-gap until the full FR-38 discovery pipeline ships.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Mapping, Optional

import hashlib

import yaml

from codexa.discovery import (
    BlastRadiusPlanner,
    BlastRadiusResult,
    DiscoveryRunRecord,
    build_repository_insights,
)
from codexa.manifest_builder import write_manifest_bundle


def _resolve_root(root: Optional[Path | str]) -> Path:
    base = Path(root) if root else Path(__file__).resolve().parents[1]
    return base.expanduser().resolve()


def _path_map(root: Path) -> dict[str, Path]:
    return {
        "CONFIG_DEFAULT": root / ".codexa/discovery/config.yaml",
        "MANIFEST_PATH": root / ".codexa/manifests/system_manifest.yaml",
        "CHANGE_ZONES_PATH": root / ".codexa/manifests/change_zones.md",
        "INTENT_MAP_PATH": root / ".codexa/manifests/intent_map.md",
        "METRICS_PATH": root / ".codexa/manifests/understanding_coverage.yaml",
        "HANDOFF_LOG_PATH": root / ".codexa/logs/handoff_discovery.jsonl",
        "GAPS_PATH": root / ".codexa/artifacts/ms02/storyboard/gaps.md",
        "HISTORY_PATH": root / ".codexa/history/discovery_runs.yaml",
        "LOOP_PLAN_PATH": root / ".codexa/loop-plan.json",
        "ITERATION_LOG_PATH": root / ".codexa/docs/status/iteration_log.md",
        "STORYBOARD_SUMMARY_PATH": root / ".codexa/artifacts/ms02/storyboard/summary.md",
    }


def _apply_root(root: Path) -> None:
    globals().update(_path_map(root))


def _apply_output_overrides(root: Path, outputs: Mapping[str, object] | None) -> None:
    if not outputs:
        return
    mapping = {
        "manifest_path": "MANIFEST_PATH",
        "change_zones_path": "CHANGE_ZONES_PATH",
        "intent_map_path": "INTENT_MAP_PATH",
        "metrics_path": "METRICS_PATH",
    }
    updates: dict[str, Path] = {}
    for key, global_name in mapping.items():
        value = outputs.get(key) if isinstance(outputs, Mapping) else None
        if not value:
            continue
        path_value = Path(str(value))
        if not path_value.is_absolute():
            path_value = root / path_value
        updates[global_name] = path_value
    if updates:
        globals().update(updates)


ROOT = _resolve_root(os.environ.get("CODEXA_PROJECT_ROOT"))
_apply_root(ROOT)


def set_project_root(root: Path | str) -> Path:
    """
    Override the project root for discovery runs.

    Returns the resolved absolute root path.
    """
    resolved = _resolve_root(root)
    globals()["ROOT"] = resolved
    _apply_root(resolved)
    return resolved

LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".md": "markdown",
    ".markdown": "markdown",
    ".mdx": "markdown",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".sh": "shell",
    ".bash": "shell",
    ".ps1": "powershell",
    ".txt": "text",
    ".rst": "rst",
    ".sql": "sql",
    ".ts": "typescript",
    ".rs": "rust",
    ".js": "javascript"
}

FOLLOWUP_PATTERN = re.compile(r"`([^`]+)`")

ZONE_SUMMARY_OVERRIDES = {
    "root": "Repository root assets",
    "agents": "Core agent orchestration and prompts",
    "pipelines": "Automation utilities and CLI adjacencies",
    "docs": "Documentation & governance records",
    "design": "Product and storyboard design assets",
    "scripts": "Operational scripts & bootstrappers",
    "tests": "Test harness and integration suites",
    "artifacts": "Generated demo collateral & run output",
    "audit": "Audit evidence & logs",
    "analysis": "Discovery analysis artifacts",
    "backlog": "Research & comparison notes",
    "changes": "Change packages & specs",
    ".codex": "Codex CLI configuration",
    ".vscode": "Workspace settings",
}


@dataclass
class ScanResult:
    language_counts: Counter
    zone_stats: dict[str, dict[str, object]]
    file_index: list[dict[str, object]]
    total_files: int
    total_bytes: int


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def git_commit_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def should_skip(path: Path, skip_prefixes: Iterable[str]) -> bool:
    path_str = str(path).replace("\\", "/")
    for prefix in skip_prefixes:
        normalized = prefix.rstrip("/")
        if not normalized:
            continue
        if path_str == normalized or path_str.startswith(f"{normalized}/"):
            return True
    return False


def matches_focus(path: Path, patterns: Iterable[str]) -> bool:
    if not patterns:
        return True
    rel = str(path).replace("\\", "/")
    return any(fnmatch.fnmatch(rel, pattern) for pattern in patterns)


def detect_language(file_path: Path) -> str:
    return LANGUAGE_BY_SUFFIX.get(file_path.suffix.lower(), "other")


def scan_repository(config: Mapping[str, object]) -> ScanResult:
    run_cfg = config.get("run", {})
    skip_paths = [str(item) for item in run_cfg.get("skip_paths", [])]
    focus_patterns = [str(item) for item in run_cfg.get("focus", [])]

    try:
        self_relative_path = Path(__file__).resolve().relative_to(ROOT)
    except ValueError:
        self_relative_path = None

    language_counts: Counter = Counter()
    zone_stats: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "file_count": 0,
            "bytes": 0,
            "languages": Counter(),
        }
    )
    file_index: list[dict[str, object]] = []

    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel_dir = Path(dirpath).resolve().relative_to(ROOT)
        if should_skip(rel_dir, skip_paths):
            dirnames[:] = []
            continue

        # Filter subdirectories in-place to respect skip prefixes.
        dirnames[:] = [
            d
            for d in dirnames
            if not should_skip(rel_dir / d, skip_paths)
        ]

        for filename in filenames:
            rel_file = (rel_dir / filename)
            if self_relative_path and rel_file == self_relative_path:
                continue
            if should_skip(rel_file, skip_paths):
                continue
            if not matches_focus(rel_file, focus_patterns):
                continue

            file_path = ROOT / rel_file
            language = detect_language(file_path)
            zone = (
                rel_file.parts[0]
                if rel_file.parts and len(rel_file.parts) > 1
                else "root"
            )
            try:
                size = file_path.stat().st_size
            except OSError:
                size = 0

            language_counts[language] += 1
            zone_stats[zone]["file_count"] += 1
            zone_stats[zone]["bytes"] += size
            zone_stats[zone]["languages"][language] += 1
            file_index.append(
                {
                    "path": str(rel_file).replace("\\", "/"),
                    "zone": zone,
                    "language": language,
                    "bytes": size,
                }
            )

    total_files = sum(language_counts.values())
    total_bytes = sum(int(data["bytes"]) for data in zone_stats.values())
    return ScanResult(
        language_counts=language_counts,
        zone_stats=zone_stats,
        file_index=file_index,
        total_files=total_files,
        total_bytes=total_bytes,
    )


def read_loop_scope() -> dict[str, object]:
    if not LOOP_PLAN_PATH.exists():
        return {}
    with LOOP_PLAN_PATH.open("r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return {}


def read_followups() -> list[str]:
    if not ITERATION_LOG_PATH.exists():
        return []
    followups: list[str] = []
    rows = [
        line
        for line in ITERATION_LOG_PATH.read_text(encoding="utf-8").splitlines()
        if line.startswith("|")
    ]
    for row in rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) < 6:
            continue
        # Header contains "Follow-ups (IDs)"
        if cells[3].lower().startswith("follow-ups"):
            continue
        if cells[0].startswith("---"):
            continue
        followup_cell = cells[3]
        if followup_cell == "—":
            continue
        for item in followup_cell.split(","):
            item = item.strip()
            if item:
                followups.append(item)
    return followups


def read_gap_followups() -> list[str]:
    if not GAPS_PATH.exists():
        return []
    ids: list[str] = []
    for line in GAPS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        for match in FOLLOWUP_PATTERN.findall(line):
            if match.startswith("issue-"):
                ids.append(match)
    return ids


def warn_followup_mismatch(iteration_followups: list[str], gap_followups: list[str]) -> None:
    iteration_set = {item for item in iteration_followups if item}
    gap_set = {item for item in gap_followups if item}
    missing = sorted(iteration_set - gap_set)
    extra = sorted(gap_set - iteration_set)
    if not missing and not extra:
        return
    messages: list[str] = []
    if missing:
        messages.append(f"Missing in gaps.md: {', '.join(missing)}")
    if extra:
        messages.append(f"Missing in iteration log: {', '.join(extra)}")
    if messages:
        sys.stderr.write("[codexa discover] Follow-up mismatch: " + "; ".join(messages) + "\n")


def load_run_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    with HISTORY_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or []
    if isinstance(data, list):
        return data
    return []


def load_previous_record() -> Optional[DiscoveryRunRecord]:
    history = load_run_history()
    if not history:
        return None
    last_entry = history[-1]
    record_payload = last_entry.get("record") if isinstance(last_entry, dict) else None
    if not isinstance(record_payload, dict):
        return None
    return DiscoveryRunRecord.from_dict(record_payload)


def append_history(
    *,
    record: DiscoveryRunRecord,
    blast_radius: BlastRadiusResult,
) -> None:
    history = load_run_history()
    history.append(
        {
            "record": record.to_dict(),
            "blast_radius": blast_radius.to_dict(),
        }
    )
    # Retain the most recent 20 entries to keep the file compact.
    history = history[-20:]
    ensure_parent(HISTORY_PATH)
    with HISTORY_PATH.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(history, handle, sort_keys=False)


def read_storyboard_metrics() -> tuple[float | None, str | None]:
    if not STORYBOARD_SUMMARY_PATH.exists():
        return None, None
    coverage: float | None = None
    freshness = None
    for line in STORYBOARD_SUMMARY_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.lower().startswith("- understanding coverage"):
            # e.g., "- Understanding coverage at 68.0%; ..."
            try:
                coverage_str = line.split("at", 1)[1].split("%", 1)[0].strip()
                coverage = float(coverage_str)
            except (IndexError, ValueError):
                pass
        if "| Discovery Freshness |" in line:
            parts = [part.strip() for part in line.split("|") if part.strip()]
            if len(parts) >= 3:
                freshness = parts[1]
    return coverage, freshness


def build_language_inventory(scan: ScanResult) -> dict[str, dict[str, object]]:
    inventory: dict[str, dict[str, object]] = {}
    for language, count in scan.language_counts.items():
        if count == 0:
            continue
        zone_language_counts = {
            zone: data["languages"][language]
            for zone, data in scan.zone_stats.items()
            if data["languages"][language] > 0
        }
        primary_paths = [
            f"{zone}/" if zone != "root" else "."
            for zone, _ in sorted(
                zone_language_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ]
        primary_paths = list(dict.fromkeys(primary_paths))
        inventory[language] = {
            "primary_paths": primary_paths or ["."],
            "notes": f"Auto-detected; {count} tracked files.",
        }
    return inventory


def deduce_zone_summary(zone: str) -> str:
    return ZONE_SUMMARY_OVERRIDES.get(zone, f"{zone.title()} assets")


def format_human_size(size_bytes: int) -> str:
    if size_bytes <= 0:
        return "0 B"
    suffixes = ["B", "KB", "MB", "GB"]
    idx = 0
    size = float(size_bytes)
    while size >= 1024 and idx < len(suffixes) - 1:
        size /= 1024
        idx += 1
    return f"{size:.1f} {suffixes[idx]}"


def dominant_language(languages: Counter) -> tuple[str, int] | tuple[None, int]:
    if not languages:
        return None, 0
    ordered = languages.most_common()
    dominant = ordered[0]
    if dominant[0] != "other":
        return dominant
    for lang, count in ordered:
        if lang != "other":
            return lang, count
    return dominant


def summarized_languages(languages: Counter, limit: int = 3) -> str:
    if not languages:
        return "mixed"
    ordered = [
        (lang, count)
        for lang, count in languages.most_common()
        if lang != "other"
    ]
    if not ordered:
        ordered = languages.most_common()
    return ", ".join(lang for lang, _ in ordered[:limit]) or "mixed"


def compute_coverage(scan: ScanResult) -> dict[str, object]:
    total_files = max(scan.total_files, 0)
    other_count = scan.language_counts.get("other", 0)
    structured_files = max(total_files - other_count, 0)
    coverage_percent = (
        round(structured_files / total_files * 100, 1) if total_files else 0.0
    )
    return {
        "total_files": total_files,
        "structured_files": structured_files,
        "other_files": other_count,
        "coverage_percent": coverage_percent,
        "language_count": sum(1 for c in scan.language_counts.values() if c > 0),
    }


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def sha256_bytes(data: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def build_metrics_data(
    scan: ScanResult,
    coverage: Mapping[str, object],
    timestamp: str,
    followups: list[str],
    artifact_hashes: Mapping[str, str],
    insights: list[dict[str, object]],
) -> dict:
    ordered_zones = sorted(
        scan.zone_stats.items(),
        key=lambda item: (item[1]["file_count"], item[1]["bytes"]),
        reverse=True,
    )
    zone_entries = []
    for zone, stats in ordered_zones:
        zone_entries.append(
            {
                "zone": zone,
                "files": int(stats["file_count"]),
                "bytes": int(stats["bytes"]),
                "languages": dict(stats["languages"].most_common(3)),
                "summary": deduce_zone_summary(zone),
            }
        )

    python_files = sum(1 for insight in insights if insight.get("language") == "python")
    total_complexity = sum(int(insight.get("complexity", 0)) for insight in insights)

    return {
        "metadata": {
            "generated_at": timestamp,
            "generator": "codexa discover",
            "commit_sha": git_commit_sha(),
        },
        "inputs": {
            "config": str(CONFIG_DEFAULT.relative_to(ROOT)),
            "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
            "change_zones": str(CHANGE_ZONES_PATH.relative_to(ROOT)),
            "intent_map": str(INTENT_MAP_PATH.relative_to(ROOT)),
            "followups_open": followups,
        },
        "coverage": coverage,
        "zones": zone_entries,
        "insights_summary": {
            "files_indexed": len(insights),
            "python_files": python_files,
            "total_complexity": total_complexity,
        },
        "artifacts": {
            "system_manifest": {
                "path": str(MANIFEST_PATH.relative_to(ROOT)),
                "sha256": artifact_hashes["system_manifest"],
            },
            "change_zones": {
                "path": str(CHANGE_ZONES_PATH.relative_to(ROOT)),
                "sha256": artifact_hashes["change_zones"],
            },
            "intent_map": {
                "path": str(INTENT_MAP_PATH.relative_to(ROOT)),
                "sha256": artifact_hashes["intent_map"],
            },
            "metrics": {
                "path": str(METRICS_PATH.relative_to(ROOT)),
                "sha256": artifact_hashes.get("metrics"),
            },
        },
    }


def render_change_zones(scan: ScanResult, timestamp: str, followups: list[str]) -> str:
    if not scan.zone_stats:
        table_rows = ["| Z-000 | Repository root | — | low | No files detected |"]
    else:
        ordered = sorted(
            scan.zone_stats.items(),
            key=lambda item: (item[1]["file_count"], item[1]["bytes"]),
            reverse=True,
        )
        table_rows = []
        for idx, (zone, stats) in enumerate(ordered, start=1):
            zone_id = f"Z-{idx:03d}"
            summary = deduce_zone_summary(zone)
            languages = stats["languages"]
            lang_name, lang_count = dominant_language(languages)
            if lang_name:
                drivers = f"{lang_name} files: {lang_count}"
            else:
                drivers = "Mixed content"
            notes = (
                f"Auto-generated {timestamp}; size {format_human_size(int(stats['bytes']))}."
            )
            confidence = "medium"
            table_rows.append(
                f"| {zone_id} | {summary} | {drivers} | {confidence} | {notes} |"
            )
    followup_note = (
        "- Active follow-ups: " + ", ".join(followups)
        if followups
        else "- Active follow-ups: none"
    )
    return "\n".join(
        [
            "# MS-02 Discovery Change Zones",
            "",
            "| Zone ID | Summary | Drivers | Confidence | Notes |",
            "| --- | --- | --- | --- | --- |",
            *table_rows,
            "",
            "## Guidance",
            "- Replace this table with analyzer output once the discovery pipeline is live.",
            "- Align zone IDs with `loop-plan.json` and `TRACEABILITY.md` entries.",
            followup_note + ".",
            "- Update drivers/notes after each `codexa discover` run.",
            "",
        ]
    )


def render_intent_map(
    scan: ScanResult, timestamp: str, followups: list[str]
) -> str:
    rows = []
    ordered_zones = sorted(
        scan.zone_stats.items(),
        key=lambda item: (item[1]["file_count"], item[1]["bytes"]),
        reverse=True,
    )
    for idx, (zone, stats) in enumerate(ordered_zones, start=1):
        intent_id = f"INT-{idx:03d}"
        description = f"{deduce_zone_summary(zone)} focus area"
        top_languages = summarized_languages(stats["languages"])
        primary_modules = f"{zone}/" if zone != "root" else "."
        followup = followups[0] if followups and idx == 1 else "—"
        rows.append(
            f"| {intent_id} | {description} | {primary_modules} | {top_languages} | {followup} |"
        )

    if not rows:
        rows.append("| INT-000 | Repository root | . | mixed | — |")

    return "\n".join(
        [
            "# MS-02 Discovery Intent Map",
            "",
            "## Capability Clusters",
            "",
            "| Intent ID | Description | Primary Modules | Detected Languages | Follow-ups |",
            "| --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Generation Notes",
            f"- Auto-generated {timestamp} via `scripts/discovery_bootstrap.py`.",
            "- Confidence values will be refined once semantic discovery is implemented.",
            "- Update follow-ups in lockstep with `docs/status/iteration_log.md`.",
            "",
        ]
    )


def build_manifest(
    config: Mapping[str, object],
    scan: ScanResult,
    followups: list[str],
    *,
    timestamp: str,
    coverage: Mapping[str, object],
    artifact_hashes: Mapping[str, str | None],
    loop_scope: Mapping[str, object] | None,
    insights: list[dict[str, object]],
) -> dict:
    storyboard_coverage, freshness = read_storyboard_metrics()
    language_inventory = build_language_inventory(scan)

    scope = loop_scope.get("scope", {}) if loop_scope else {}
    scope_notes = loop_scope.get("notes", []) if loop_scope else []

    readiness_note = (
        f"Bootstrap manifest generated automatically at {timestamp}."
        if followups
        else f"Bootstrap manifest generated automatically; no outstanding follow-ups."
    )

    manifest = {
        "metadata": {
            "version": "0.2.0",
            "generated_at": timestamp,
            "repo": ROOT.name,
            "commit_sha": git_commit_sha(),
            "generator": "codexa discover",
            "discovery_mode": config.get("run", {}).get("mode", "full"),
            "status": "draft" if followups else "current",
            "owners": config.get("metadata", {}).get("owners", {}),
        },
        "inputs": {
            "config_file": {
                "path": str(CONFIG_DEFAULT.relative_to(ROOT)),
                "exists": CONFIG_DEFAULT.exists(),
                "todo": (
                    "Validate against discovery CLI once FR-38 is implemented."
                ),
            },
            "loop_scope": {
                "path": str(LOOP_PLAN_PATH.relative_to(ROOT)),
                "scope_id": scope.get("id"),
                "scope_type": scope.get("type"),
                "description": scope.get("description"),
                "captured_at": loop_scope.get("source", {}).get("captured_at")
                if loop_scope
                else None,
            },
            "reference_docs": [
                "design/MS-02_storyboard.md",
                "TRACEABILITY.md",
                "docs/ARCHITECTURE.md",
                "docs/PROJECT_OVERVIEW.md",
                str(ITERATION_LOG_PATH.relative_to(ROOT)),
            ],
            "followups_open": followups,
            "notes": scope_notes,
        },
        "summary": {
            "project_phase": "MS-02 — Discovery MVP",
            "readiness": {
                "discovery_artifacts_present": True,
                "iteration_followups_open": bool(followups),
                "notes": readiness_note,
            },
            "understanding_metrics": {
                "coverage_percent": coverage.get("coverage_percent"),
                "coverage_source": str(
                    METRICS_PATH.relative_to(ROOT)
                ),
                "coverage_previous": storyboard_coverage,
                "discovery_freshness": freshness or timestamp,
                "freshness_source": str(
                    STORYBOARD_SUMMARY_PATH.relative_to(ROOT)
                )
                if STORYBOARD_SUMMARY_PATH.exists()
                else None,
            },
            "discovery_artifacts": {
                "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
                "change_zones": str(CHANGE_ZONES_PATH.relative_to(ROOT)),
                "intent_map": str(INTENT_MAP_PATH.relative_to(ROOT)),
                "config_template": str(CONFIG_DEFAULT.relative_to(ROOT)),
                "artifact_hashes": {
                    "change_zones": artifact_hashes.get("change_zones"),
                    "intent_map": artifact_hashes.get("intent_map"),
                },
                "metrics": str(METRICS_PATH.relative_to(ROOT)),
            },
            "language_inventory": language_inventory,
            "toolchain": {
                "python_version": "3.11",
                "static_analysis": [
                    "tree-sitter (planned)",
                    "tokei",
                    "radon",
                    "pygount",
                ],
                "orchestration": [
                    "codexa CLI (planned)",
                    "Makefile targets",
                ],
            },
        },
        "architecture": {
            "layers": [
                {
                    "name": "Agent Orchestration",
                    "responsibilities": [
                        "Coordinate milestone loops (PM → Designer → Implementer → Tester).",
                        "Maintain audit handoffs and approvals.",
                    ],
                    "components": [
                        {"path": "agents/project_manager.py"},
                        {"path": "pipelines/phase1_orchestrator.py"},
                    ],
                },
                {
                    "name": "Discovery & Understanding",
                    "responsibilities": [
                        "Produce structural manifests and iteration logs.",
                        "Drive System Model Graph refresh (planned).",
                    ],
                    "components": [
                        {"path": "scripts/discovery_bootstrap.py"},
                        {"path": "scripts/ms02_dry_run.py"},
                        {"path": "docs/status/iteration_log.md"},
                    ],
                },
                {
                    "name": "Audit & Governance",
                    "responsibilities": [
                        "Persist commands, handoffs, approvals, and QA evidence.",
                        "Surface governance snapshots.",
                    ],
                    "components": [
                        {"path": "audit/commands.jsonl"},
                        {"path": "audit/handoff_ms01_phase0.jsonl"},
                        {"path": "artifacts/ms02/storyboard/gaps.md"},
                    ],
                },
                {
                    "name": "Execution & QA",
                    "responsibilities": [
                        "Provide deterministic execution paths and QA policy enforcement."
                    ],
                    "components": [
                        {"path": "pipelines/qa_enforcer.py"},
                        {"path": "tests/"},
                    ],
                },
            ]
        },
        "components": [
            {
                "id": "agents",
                "name": "Core Agents",
                "paths": [
                    "agents/project_manager.py",
                    "agents/designer.py",
                    "agents/implementer.py",
                    "agents/tester.py",
                ],
                "responsibilities": [
                    "Orchestrate milestone workflows and generate documentation.",
                    "Provide deterministic outputs for demos.",
                ],
                "dependencies": [
                    "pipelines.audit",
                    "pipelines.interaction_stub",
                ],
                "maturity": "phase0-stable",
                "requirements": ["FR-01", "FR-04", "FR-06"],
                "trace_links": [
                    "TRACEABILITY.md#ws-101-multi-agent-orchestration",
                    "TRACEABILITY.md#phase-0-foundation",
                ],
            },
            {
                "id": "pipelines",
                "name": "Pipeline Utilities",
                "paths": ["pipelines/"],
                "responsibilities": [
                    "Provide CLI-adjacent tooling (interaction stub, concern tools, orchestrator, status snapshots)."
                ],
                "dependencies": [
                    "audit.logger",
                    "QA_POLICY.yaml",
                ],
                "maturity": "mixed",
                "requirements": ["FR-38", "FR-41"],
                "trace_links": [
                    "TRACEABILITY.md#ws-09-discovery-foundations",
                    "TRACEABILITY.md#fr-41-understanding-coverage-readiness-metrics",
                ],
            },
            {
                "id": "discovery-seeding",
                "name": "Discovery Seed Artifacts",
                "paths": [
                    "scripts/discovery_bootstrap.py",
                    "scripts/ms02_dry_run.py",
                    "artifacts/ms02/storyboard/",
                    "docs/status/iteration_log.md",
                ],
                "responsibilities": [
                    "Simulate discovery outputs until full pipeline ships.",
                    "Supply governance summaries and gaps tracking.",
                ],
                "dependencies": [
                    "loop-plan.json",
                    "TRACEABILITY.md",
                ],
                "maturity": "provisional",
                "requirements": ["FR-38", "FR-40", "FR-41"],
                "trace_links": [
                    "TRACEABILITY.md#ws-09-discovery-foundations",
                    "TRACEABILITY.md#ws-110-loop-planning-seed-generation",
                ],
            },
            {
                "id": "governance-docs",
                "name": "Governance & Traceability",
                "paths": [
                    "TRACEABILITY.md",
                    "docs/PROJECT_OVERVIEW.md",
                    "docs/ARCHITECTURE.md",
                ],
                "responsibilities": [
                    "Maintain milestone, workstream, and requirement status.",
                    "Provide human-readable overviews and approvals.",
                ],
                "dependencies": [
                    "audit/commands.jsonl",
                    "changes/",
                ],
                "maturity": "evolving",
                "requirements": ["FR-02", "FR-10", "FR-13"],
                "trace_links": [
                    "TRACEABILITY.md#phase-0-foundation",
                    "TRACEABILITY.md#ms-02--discovery-mvp",
                ],
            },
        ],
        "analysis": {
            "repository_insights": insights,
        },
        "artifacts": {
            "audit_trail": {
                "command_log": "audit/commands.jsonl",
                "handoffs": [
                    "audit/handoff.jsonl",
                    "audit/handoff_ms01_phase0.jsonl",
                    "audit/handoff_discovery.jsonl",
                ],
            },
            "discovery_snapshots": {
                "storyboard_summary": "artifacts/ms02/storyboard/summary.md",
                "gaps": "artifacts/ms02/storyboard/gaps.md",
                "iteration_log": "docs/status/iteration_log.md",
                "change_zones": "analysis/change_zones.md",
                "intent_map": "analysis/intent_map.md",
            },
            "milestone_assets": {
                "storyboard": "design/MS-02_storyboard.md",
                "governance": "artifacts/ms02/storyboard/summary.md",
                "change_scope": "loop-plan.json",
            },
            "change_work": {
                "active_changes": ["changes/CH-001/"],
                "planned_changes": ["CH-010 (loop plan)"],
            },
        },
        "dependencies_external": {
            "python_modules": ["argparse", "yaml", "json", "pathlib"],
            "cli_tools": ["make", "git"],
            "analysis_tooling_planned": [
                "tree-sitter",
                "tokei",
                "radon",
                "pygount",
            ],
        },
        "risks_and_gaps": [
            {
                "id": "gap-issue-12",
                "description": "Follow-up issue-12 remains open from discovery dry run.",
                "mitigation": "Resolve via conversational follow-up or rerun discovery once manifests are real.",
                "status": "open" if followups else "closed",
            },
            {
                "id": "gap-automation",
                "description": "Automated manifest generation (FR-38) not fully implemented; bootstrap script lacks semantic analysis.",
                "mitigation": "Integrate discovery analyzer agent and CLI pipeline.",
                "status": "open",
            },
        ],
        "next_actions": [
            "Implement tree-sitter backed analysis for structural graphs (FR-38).",
            "Add manifest hashing and System Model Graph pointers.",
            "Replace bootstrap script with production discovery analyzer.",
        ],
    }
    return manifest


def render_manifest_yaml(manifest: dict) -> str:
    header = "# Auto-generated by codexa discover; do not edit manually.\n"
    body = yaml.safe_dump(manifest, sort_keys=False)
    return header + body


def write_text(path: Path, content: str) -> None:
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")


def append_handoff_entry(
    *,
    timestamp: str,
    loop_scope: Mapping[str, object] | None,
    mode: str,
    followups: list[str],
    artifact_hashes: Mapping[str, str | None],
) -> None:
    scope = loop_scope.get("scope", {}) if loop_scope else {}
    artifact_entries = []
    for key, path in (
        ("system_manifest", MANIFEST_PATH),
        ("change_zones", CHANGE_ZONES_PATH),
        ("intent_map", INTENT_MAP_PATH),
        ("metrics", METRICS_PATH),
    ):
        digest = artifact_hashes.get(key)
        if digest is None:
            continue
        artifact_entries.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": digest,
            }
        )

    entry = {
        "timestamp": timestamp,
        "from": "project_manager",
        "to": "discovery_analyzer",
        "summary": "Discovery bootstrap artifacts generated for MS-02 Phase 0.",
        "artifacts": artifact_entries,
        "metadata": {
            "change_id": scope.get("id"),
            "scope_type": scope.get("type"),
            "mode": mode,
            "followups_open": followups,
            "generator": "scripts/discovery_bootstrap.py",
        },
    }

    ensure_parent(HANDOFF_LOG_PATH)
    with HANDOFF_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def _emit_progress(callback, percent: int, message: str) -> None:
    if not callback:
        return
    try:
        callback(int(percent), message)
    except Exception:
        # Progress updates should never break a discovery run.
        pass


def run_discovery(
    config_path: Path | None = None,
    *,
    mode_override: Optional[str] = None,
    log_handoff: Optional[bool] = None,
    track_history: bool = True,
    project_root: Path | str | None = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> dict:
    """Execute the discovery workflow and return a summary dictionary."""
    if project_root:
        set_project_root(project_root)

    _emit_progress(progress_callback, 5, "Loading discovery config…")
    config_path = Path(config_path) if config_path else CONFIG_DEFAULT
    if not config_path.is_absolute():
        config_path = ROOT / config_path
    config = load_config(config_path)

    _apply_output_overrides(ROOT, config.get("outputs"))

    if mode_override:
        config.setdefault("run", {})["mode"] = mode_override

    loop_scope = read_loop_scope()
    followups = read_followups()
    gap_followups = read_gap_followups()
    if config.get("audit", {}).get("log_followups", True):
        warn_followup_mismatch(followups, gap_followups)

    default_log_handoff = bool(config.get("audit", {}).get("write_handoff", False))
    if log_handoff is None:
        log_handoff = default_log_handoff

    _emit_progress(progress_callback, 15, "Scanning repository…")
    scan = scan_repository(config)
    _emit_progress(progress_callback, 30, "Computing coverage and insights…")
    timestamp = now_iso()
    coverage = compute_coverage(scan)
    insights = build_repository_insights(scan.file_index, root=ROOT)
    mode = config.get("run", {}).get("mode", "full")

    change_zones_content = render_change_zones(scan, timestamp, followups)
    change_zones_hash = sha256_text(change_zones_content)
    intent_map_content = render_intent_map(scan, timestamp, followups)
    intent_map_hash = sha256_text(intent_map_content)

    artifact_hashes: dict[str, str | None] = {
        "change_zones": change_zones_hash,
        "intent_map": intent_map_hash,
        "metrics": None,
    }

    _emit_progress(progress_callback, 50, "Building manifests and reports…")
    manifest = build_manifest(
        config,
        scan,
        followups,
        timestamp=timestamp,
        coverage=coverage,
        artifact_hashes=artifact_hashes,
        loop_scope=loop_scope,
        insights=insights,
    )
    manifest_content = render_manifest_yaml(manifest)
    manifest_hash = sha256_text(manifest_content)
    artifact_hashes["system_manifest"] = manifest_hash

    _emit_progress(progress_callback, 65, "Computing coverage metrics…")
    metrics_data = build_metrics_data(
        scan,
        coverage,
        timestamp,
        followups,
        artifact_hashes,
        insights,
    )
    metrics_content = yaml.safe_dump(metrics_data, sort_keys=False)
    metrics_hash = sha256_text(metrics_content)
    artifact_hashes["metrics"] = metrics_hash

    _emit_progress(progress_callback, 75, "Writing artifacts to disk…")
    write_text(CHANGE_ZONES_PATH, change_zones_content)
    write_text(INTENT_MAP_PATH, intent_map_content)
    write_text(MANIFEST_PATH, manifest_content)
    write_text(METRICS_PATH, metrics_content)

    domains = write_manifest_bundle(
        ROOT,
        file_index=scan.file_index,
        generated_at=timestamp,
    )

    record = DiscoveryRunRecord.from_metrics(metrics_data)
    planner = BlastRadiusPlanner()
    previous_record = load_previous_record() if track_history else None
    _emit_progress(progress_callback, 85, "Planning blast radius…")
    radius_result = planner.plan(record, previous_record)

    if track_history:
        append_history(record=record, blast_radius=radius_result)

    if log_handoff:
        _emit_progress(progress_callback, 92, "Updating audit trail…")
        append_handoff_entry(
            timestamp=timestamp,
            loop_scope=loop_scope,
            mode=mode,
            followups=list(followups),
            artifact_hashes=artifact_hashes,
        )

    result = {
        "timestamp": timestamp,
        "mode": mode,
        "coverage": coverage,
        "paths": {
            "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
            "change_zones": str(CHANGE_ZONES_PATH.relative_to(ROOT)),
            "intent_map": str(INTENT_MAP_PATH.relative_to(ROOT)),
            "metrics": str(METRICS_PATH.relative_to(ROOT)),
        },
        "artifact_hashes": artifact_hashes,
        "blast_radius": radius_result.to_dict(),
        "record": record.to_dict(),
        "insights": insights,
        "inferred_domains": [domain.to_dict() for domain in domains],
    }

    _emit_progress(progress_callback, 100, "Discovery complete.")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=None,
        type=Path,
        help="Path to discovery configuration (YAML).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Repository root to analyse (defaults to the directory containing this script).",
    )
    parser.add_argument(
        "--log-handoff",
        dest="log_handoff",
        action="store_true",
        help="Append an entry to audit/handoff_discovery.jsonl",
    )
    parser.add_argument(
        "--no-log-handoff",
        dest="log_handoff",
        action="store_false",
        help="Disable audit handoff logging for this run",
    )
    parser.set_defaults(log_handoff=None)
    args = parser.parse_args()

    result = run_discovery(
        config_path=args.config,
        log_handoff=args.log_handoff,
        project_root=args.root,
    )

    print("Discovery artifacts generated:")
    for label, path in result["paths"].items():
        print(f" - {path}")

    radius = result["blast_radius"]
    changed_zones = radius.get("changed_zones") or []
    recommended_agents = radius.get("recommended_agents") or []
    print(
        f"Blast radius level: {radius['level']} "
        f"(zones: {', '.join(changed_zones) if changed_zones else 'none'})"
    )
    if recommended_agents:
        print(f"Recommended agents: {', '.join(recommended_agents)}")
    coverage_percent = result["coverage"].get("coverage_percent", 0.0)
    print(f"Coverage snapshot: {coverage_percent:.1f}%")


if __name__ == "__main__":
    main()
