"""Unified manifest builder for the adaptive discovery pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional


SEMANTIC_PATH = Path(".codexa/discovery/manifest_semantic.json")
INTERFACE_PATH = Path(".codexa/discovery/manifest_surface.json")
SYSTEM_PATH = Path(".codexa/discovery/manifest_system.json")
OUTPUT_PATH = Path(".codexa/discovery/manifest.json")
logger = logging.getLogger("codexa.discovery.manifest")


@dataclass
class ModuleEntry:
    file: str
    summary: str
    entities: List[str]
    responsibilities: List[str]
    dependencies: List[str]
    confidence: float
    model: str
    tier: str
    latency_s: float
    cached: bool
    last_updated: str


@dataclass
class DiscoveryManifest:
    version: str
    generated_at: str
    modules: List[ModuleEntry]
    interfaces: List[Mapping[str, object]]
    subsystems: List[Mapping[str, object]]
    stats: Mapping[str, object]


def load_manifest_json(path: Path) -> Optional[object]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _index_by_file(entries: Iterable[Mapping[str, object]]) -> Dict[str, Mapping[str, object]]:
    index: Dict[str, Mapping[str, object]] = {}
    for entry in entries:
        path = entry.get("file")
        if isinstance(path, str):
            index[path] = entry
    return index


def _to_module_entry(payload: Mapping[str, object], *, timestamp: str) -> ModuleEntry:
    return ModuleEntry(
        file=str(payload.get("file", "")),
        summary=str(payload.get("summary", "")),
        entities=list(payload.get("entities") or []),
        responsibilities=list(payload.get("responsibilities") or []),
        dependencies=list(payload.get("dependencies") or []),
        confidence=float(payload.get("confidence") or 0.0),
        model=str(payload.get("model", "")),
        tier=str(payload.get("tier", "")),
        latency_s=float(payload.get("latency_s") or 0.0),
        cached=bool(payload.get("cached", False)),
        last_updated=timestamp,
    )


def build_manifest(
    *,
    semantic_path: Path = SEMANTIC_PATH,
    interface_path: Path = INTERFACE_PATH,
    system_path: Path = SYSTEM_PATH,
    output_path: Path = OUTPUT_PATH,
    extra_stats: Optional[Mapping[str, object]] = None,
) -> DiscoveryManifest:
    semantic_payload = load_manifest_json(semantic_path) or []
    interface_payload = load_manifest_json(interface_path) or []
    system_payload = load_manifest_json(system_path) or {}
    timestamp = datetime.utcnow().isoformat()

    modules = []
    module_index = _index_by_file(semantic_payload)
    for file_path, data in sorted(module_index.items()):
        modules.append(_to_module_entry(data, timestamp=timestamp))

    average_conf = (
        sum(entry.confidence for entry in modules) / max(len(modules), 1)
        if modules
        else 0.0
    )

    tiers: Dict[str, int] = {}
    total_latency = 0.0
    cached_count = 0
    for entry in modules:
        tiers[entry.tier] = tiers.get(entry.tier, 0) + 1
        total_latency += entry.latency_s
        if entry.cached:
            cached_count += 1

    interface_entries = list(interface_payload) if isinstance(interface_payload, list) else []
    interface_count = len(interface_entries)
    iface_stats = _aggregate_interface_stats(interface_entries)

    manifest = DiscoveryManifest(
        version="1.0",
        generated_at=timestamp,
        modules=modules,
        interfaces=interface_entries,
        subsystems=list(system_payload.get("subsystems") or []),
        stats={
            "module_count": len(modules),
            "average_confidence": round(average_conf, 3),
            "tier_breakdown": tiers,
            "latency_total_s": round(total_latency, 3),
            "cached_modules": cached_count,
            "interface_entries": interface_count,
            **iface_stats,
        },
    )

    if extra_stats:
        manifest.stats = dict(manifest.stats)
        for key, value in extra_stats.items():
            manifest.stats[key] = value

    serialised = {
        "version": manifest.version,
        "generated_at": manifest.generated_at,
        "modules": [asdict(entry) for entry in manifest.modules],
        "interfaces": manifest.interfaces,
        "subsystems": manifest.subsystems,
        "stats": manifest.stats,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(serialised, indent=2), encoding="utf-8")
    logger.info(
        "Discovery manifest persisted to %s (modules=%d, interfaces=%d, subsystems=%d)",
        output_path,
        len(manifest.modules),
        len(manifest.interfaces),
        len(manifest.subsystems),
    )
    return manifest


__all__ = ["ModuleEntry", "DiscoveryManifest", "build_manifest", "load_manifest_json"]


def _aggregate_interface_stats(entries: List[Mapping[str, object]]) -> Dict[str, int]:
    totals = {
        "interface_cli_commands": 0,
        "interface_api_endpoints": 0,
        "interface_config_files": 0,
        "interface_test_cases": 0,
        "interface_doc_examples": 0,
    }
    for entry in entries:
        totals["interface_cli_commands"] += len(entry.get("cli_commands") or [])
        totals["interface_api_endpoints"] += len(entry.get("api_endpoints") or [])
        totals["interface_config_files"] += len(entry.get("config_files") or [])
        totals["interface_test_cases"] += len(entry.get("test_cases") or [])
        totals["interface_doc_examples"] += len(entry.get("doc_examples") or [])
    return totals
