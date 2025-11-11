"""Generate structured manifest artifacts from discovery insights."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Mapping


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


@dataclass
class DomainSummary:
    name: str
    path: str
    kind: str
    file_count: int
    languages: Mapping[str, int]
    description: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "kind": self.kind,
            "file_count": self.file_count,
            "languages": dict(self.languages),
            "description": self.description,
        }


def _classify_kind(zone: str, language_counts: Mapping[str, int]) -> str:
    zone_lower = zone.lower()
    total = sum(language_counts.values()) or 1
    python_ratio = language_counts.get("python", 0) / total
    markdown_ratio = language_counts.get("markdown", 0) / total

    if zone_lower in {"tests", "testing"} or "test" in zone_lower:
        return "tests"
    if zone_lower in {"docs", "docs_src", "documentation"} or markdown_ratio >= 0.5:
        return "docs"
    if zone_lower in {"scripts", "tools", "bin"}:
        return "automation"
    if zone_lower in {"data", "datasets"}:
        return "data"
    if python_ratio >= 0.4:
        return "code"
    if markdown_ratio >= 0.4:
        return "docs"
    return "assets"


def _kind_description(kind: str) -> str:
    return {
        "code": "Primary product code and frameworks.",
        "docs": "Documentation sources and published guides.",
        "tests": "Automated tests and fixtures.",
        "automation": "Operational scripts and tooling.",
        "data": "Data assets bundled with the project.",
        "assets": "Supporting assets (config, media, or misc).",
    }.get(kind, "Project resources.")


def _custom_description(zone: str, kind: str) -> str | None:
    zone_lower = zone.lower()
    custom_map = {
        "typer": "Typer package: Python type-hint driven CLI framework core.",
        "typer-cli": "Typer CLI wrapper: command that exposes Typer apps from the terminal.",
        "tests": "Integration and tutorial coverage for the CLI framework.",
        "scripts": "Automation scripts for docs, publishing, and maintenance.",
        "docs": "Published documentation content authored with MkDocs.",
        "docs_src": "Source material for Typer documentation and tutorials.",
    }
    return custom_map.get(zone_lower)


def infer_domains(file_index: Iterable[Mapping[str, object]]) -> List[DomainSummary]:
    stats: dict[str, dict[str, object]] = {}
    for entry in file_index:
        path = entry.get("path")
        language = entry.get("language")
        if not isinstance(path, str):
            continue
        zone = path.split("/", 1)[0] if "/" in path else path
        if zone.startswith(".") and zone not in {".github", ".vscode"}:
            continue
        zone_stat = stats.setdefault(zone, {"count": 0, "languages": {}})
        zone_stat["count"] = zone_stat.get("count", 0) + 1
        if isinstance(language, str):
            lang_counts = zone_stat.setdefault("languages", {})
            lang_counts[language] = lang_counts.get(language, 0) + 1

    summaries: List[DomainSummary] = []
    for zone, data in stats.items():
        file_count = int(data.get("count", 0))
        if file_count == 0:
            continue
        languages = data.get("languages", {})
        kind = _classify_kind(zone, languages)
        description = _custom_description(zone, kind) or _kind_description(kind)
        name = zone.replace("_", " ").replace("-", " ").title()
        summaries.append(
            DomainSummary(
                name=name,
                path=zone,
                kind=kind,
                file_count=file_count,
                languages=languages,
                description=description,
            )
        )

    summaries.sort(key=lambda d: d.file_count, reverse=True)
    return summaries


def describe_project(domains: List[DomainSummary | Mapping[str, object]]) -> str | None:
    if not domains:
        return None
    def _extract(domain):
        if isinstance(domain, DomainSummary):
            return domain
        return DomainSummary(
            name=str(domain.get("name", domain.get("path", "Domain"))).title(),
            path=str(domain.get("path", "")),
            kind=str(domain.get("kind", "domain")),
            file_count=int(domain.get("file_count", 0)),
            languages=domain.get("languages", {}),
            description=str(domain.get("description", "")),
        )

    dense = [_extract(d) for d in domains]
    primary = dense[0]
    return (
        f"Project appears centered on {primary.path} ({primary.kind}) "
        f"with {primary.file_count} tracked files; supporting domains: "
        + ", ".join(domain.path for domain in dense[1:4])
        if len(dense) > 1
        else f"Project appears centered on {primary.path} ({primary.kind})."
    )


def write_manifest_bundle(
    project_root: Path,
    *,
    file_index: Iterable[Mapping[str, object]],
    generated_at: str,
) -> List[DomainSummary]:
    project_root = project_root.expanduser().resolve()
    manifest_root = project_root / ".codexa" / "manifest"
    _ensure_dir(manifest_root)

    domains = infer_domains(file_index)

    domains_payload = {"domains": [domain.to_dict() for domain in domains]}
    (manifest_root / "domains.json").write_text(
        json.dumps(domains_payload, indent=2), encoding="utf-8"
    )

    milestones_payload = {
        "milestones": [
            {
                "id": "MS-AUTO-001",
                "name": "Auto-generated Discovery Baseline",
                "generated_at": generated_at,
            }
        ]
    }
    (manifest_root / "milestones.json").write_text(
        json.dumps(milestones_payload, indent=2), encoding="utf-8"
    )

    requirements_root = manifest_root / "requirements"
    _ensure_dir(requirements_root)
    for idx, domain in enumerate(domains[:5], start=1):
        requirement_payload = {
            "id": f"FR-{idx:02d}",
            "title": f"Baseline understanding for {domain.path}",
            "domain": domain.path,
            "status": "discovered",
            "summary": domain.description,
            "file_count": domain.file_count,
            "generated_at": generated_at,
        }
        (requirements_root / f"FR-{idx:02d}.json").write_text(
            json.dumps(requirement_payload, indent=2), encoding="utf-8"
        )

    index_payload = {
        "generated_at": generated_at,
        "domains_file": "domains.json",
        "milestones_file": "milestones.json",
        "requirements_path": "requirements/",
        "domain_count": len(domains),
    }
    (manifest_root / "index.json").write_text(
        json.dumps(index_payload, indent=2), encoding="utf-8"
    )

    return domains
