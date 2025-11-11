"""Render human-friendly reports from discovery artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable

import yaml


MANIFEST_DIR = Path(".codexa/manifest")
MANIFESTS_DIR = Path(".codexa/manifests")


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return {}
    return data or {}


def _format_domain_block(domains: Iterable[Dict[str, Any]]) -> str:
    lines = ["## 🌐 Domains"]
    for domain in domains:
        lines.append(
            f"- **{domain.get('path')}** (`{domain.get('kind')}`) — "
            f"{domain.get('description') or ''}"
        )
        lines.append(
            f"  - Files: {domain.get('file_count')} | Languages: "
            + ", ".join(
                f"{lang} ({count})" for lang, count in (domain.get('languages') or {}).items()
            )
        )
    if len(lines) == 1:
        lines.append("No domain data found. Run `codexa discover` first.")
    return "\n".join(lines)


def _format_requirements_block(requirements_dir: Path) -> str:
    lines = ["## 📋 Inferred Requirements"]
    if not requirements_dir.exists():
        lines.append("No inferred requirements yet.")
        return "\n".join(lines)

    for path in sorted(requirements_dir.glob("FR-*.json")):
        payload = _load_json(path)
        lines.append(f"- **{payload.get('id')}** — {payload.get('title')}")
        lines.append(f"  - Domain: `{payload.get('domain')}`")
        lines.append(f"  - Summary: {payload.get('summary')}")
    return "\n".join(lines)


def _format_architecture_block(system_manifest: Dict[str, Any]) -> str:
    lines = ["## 🏗️ Architecture Snapshot"]
    layers = system_manifest.get("architecture", {}).get("layers", [])
    if not layers:
        lines.append("Architecture details not available.")
        return "\n".join(lines)

    for layer in layers:
        lines.append(f"- **{layer.get('name')}**")
        responsibilities = layer.get("responsibilities", [])
        if responsibilities:
            lines.append("  - Responsibilities:")
            for responsibility in responsibilities:
                lines.append(f"    - {responsibility}")
        components = layer.get("components", [])
        if components:
            lines.append("  - Components:")
            for component in components:
                path = component.get("path") if isinstance(component, dict) else component
                lines.append(f"    - `{path}`")
    return "\n".join(lines)


def _format_summary(system_manifest: Dict[str, Any]) -> str:
    summary = system_manifest.get("summary", {})
    coverage = summary.get("understanding_metrics", {}).get("coverage_percent")
    project_phase = summary.get("project_phase")
    freshness = summary.get("understanding_metrics", {}).get("discovery_freshness")

    lines = ["# Codexa Discovery Report"]
    lines.append("")
    lines.append("## 🚀 Snapshot")
    if project_phase:
        lines.append(f"- Project phase: **{project_phase}**")
    if coverage is not None:
        lines.append(f"- Coverage: **{coverage:.1f}%**")
    if freshness:
        lines.append(f"- Freshness: {freshness}")
    lines.append("")
    return "\n".join(lines)


def generate_markdown_report(project_root: Path) -> Path:
    project_root = project_root.expanduser().resolve()
    domains_payload = _load_json(project_root / MANIFEST_DIR / "domains.json")
    domains = domains_payload.get("domains") or []
    system_manifest = _load_yaml(project_root / MANIFESTS_DIR / "system_manifest.yaml")

    report_lines = [_format_summary(system_manifest)]
    report_lines.append(_format_domain_block(domains))
    report_lines.append(
        _format_requirements_block(project_root / MANIFEST_DIR / "requirements")
    )
    report_lines.append(_format_architecture_block(system_manifest))

    report_content = "\n\n".join(report_lines) + "\n"

    report_dir = project_root / ".codexa" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "discovery_report.md"
    report_path.write_text(report_content, encoding="utf-8")
    return report_path
