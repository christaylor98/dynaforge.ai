"""Generate human-readable reports for discovery runs."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Iterable, List, Mapping

from .focus import load_focus_context


MANIFEST_PATH = Path(".codexa/discovery/manifest.json")
REPORT_PATH = Path(".codexa/discovery/report.md")
logger = logging.getLogger("codexa.discovery.reporter")


@dataclass
class ReportSection:
    title: str
    lines: List[str]

    def render(self) -> str:
        body = "\n".join(self.lines)
        return f"## {self.title}\n{body}\n"


def _load_manifest(path: Path) -> Mapping[str, object]:
    if not path.exists():
        return {}
    import json

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _low_confidence(modules: Iterable[Mapping[str, object]], threshold: float = 0.75) -> List[Mapping[str, object]]:
    results = []
    for entry in modules:
        confidence = entry.get("confidence")
        if isinstance(confidence, (int, float)) and confidence < threshold:
            results.append(entry)
    return results


def _tier_breakdown(stats: Mapping[str, object]) -> str:
    tiers = stats.get("tier_breakdown") or {}
    items = [f"{tier}: {count}" for tier, count in sorted(tiers.items())]
    return " | ".join(items) if items else "No tier data"


def build_report(manifest_path: Path = MANIFEST_PATH, report_path: Path = REPORT_PATH) -> Path:
    manifest = _load_manifest(manifest_path)
    modules: List[Mapping[str, object]] = list(manifest.get("modules") or [])
    subsystems: List[Mapping[str, object]] = list(manifest.get("subsystems") or [])
    interfaces: List[Mapping[str, object]] = list(manifest.get("interfaces") or [])
    stats: Mapping[str, object] = manifest.get("stats") or {}

    summary_lines = [
        f"- Modules analysed: {len(modules)}",
        f"- Average confidence: {stats.get('average_confidence', 0.0):.2f}",
        f"- Model tiers: {_tier_breakdown(stats)}",
        f"- Subsystems discovered: {len(subsystems)}",
    ]
    if "model_policy" in stats:
        summary_lines.append(f"- Model policy: {stats['model_policy']}")
    if "latency_total_s" in stats:
        summary_lines.append(f"- Total summarisation latency: {stats['latency_total_s']} s")
    if "cached_modules" in stats:
        summary_lines.append(f"- Cached modules reused: {stats['cached_modules']}")
    if "interface_entries" in stats:
        summary_lines.append(f"- Interface entries discovered: {stats['interface_entries']}")
    if stats.get("interface_cli_commands"):
        summary_lines.append(f"  • CLI commands: {stats['interface_cli_commands']} | API endpoints: {stats.get('interface_api_endpoints', 0)}")
    if stats.get("interface_test_cases") or stats.get("interface_doc_examples"):
        summary_lines.append(
            f"  • Test cases: {stats.get('interface_test_cases', 0)} | Doc examples: {stats.get('interface_doc_examples', 0)}"
        )

    subsystem_lines = ["Subsystem | Modules | Purpose", "--- | --- | ---"]
    for subsystem in subsystems:
        name = subsystem.get("subsystem", "(unknown)")
        module_count = len(subsystem.get("modules") or [])
        purpose = subsystem.get("purpose", "")
        subsystem_lines.append(f"{name} | {module_count} | {purpose}")
    if len(subsystem_lines) == 2:
        subsystem_lines.append("(no subsystem synthesis available)")

    low_conf = _low_confidence(modules)
    uncertain_lines: List[str] = []
    if low_conf:
        for entry in low_conf:
            file_path = entry.get("file", "(unknown)")
            confidence = entry.get("confidence", 0.0)
            summary = entry.get("summary", "")[:120]
            uncertain_lines.append(f"- `{file_path}` — {confidence:.2f} confidence — {summary}")
    else:
        uncertain_lines.append("- No modules flagged below confidence threshold.")

    next_steps = [
        "- Review low-confidence modules and provide focus notes for the next run.",
        "- Consider running `codexa discover --update` after addressing feedback.",
    ]

    focus_context = load_focus_context()
    focus_lines: List[str] = []
    if focus_context:
        if focus_context.auto_focus:
            focus_lines.append("Priority modules (low confidence):")
            focus_lines.extend(f"- {path}" for path in focus_context.auto_focus)
        if focus_context.user_notes.strip():
            focus_lines.append("User-supplied focus notes were applied this run.")
    if not focus_lines:
        focus_lines.append("No focus directives captured. Add notes via --focus or focus notes file.")

    interface_lines = ["File | Summary", "--- | ---"]
    for entry in interfaces[:8]:
        file_path = entry.get("file", "(unknown)")
        cli_count = len(entry.get("cli_commands") or [])
        api_count = len(entry.get("api_endpoints") or [])
        summary = entry.get("summary", "")[:60]
        details: List[str] = []
        if cli_count:
            details.append(f"{cli_count} CLI")
        if api_count:
            details.append(f"{api_count} API")
        if entry.get("config_files"):
            details.append(f"{len(entry['config_files'])} config")
        if entry.get("test_cases"):
            details.append(f"{len(entry['test_cases'])} tests")
        if entry.get("doc_examples"):
            details.append(f"{len(entry['doc_examples'])} docs")
        detail_text = ", ".join(details) or summary
        interface_lines.append(f"{file_path} | {detail_text}")
    if len(interface_lines) == 2:
        interface_lines.append("(no interface entries discovered yet)")

    sections = [
        ReportSection("🧠 Discovery Snapshot", summary_lines),
        ReportSection("🏗️ Subsystems", subsystem_lines),
        ReportSection("🔌 Interface Snapshot", interface_lines),
        ReportSection("⚠️ Requires Review", uncertain_lines),
        ReportSection("🎯 Focus Guidance", focus_lines),
        ReportSection("🧭 Suggested Next Steps", next_steps),
    ]

    content = ["# Discovery Report\n"]
    content.extend(section.render() for section in sections)
    rendered = "\n".join(content)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(rendered, encoding="utf-8")
    logger.info(
        "Discovery report written to %s (modules=%d, subsystems=%d, interfaces=%d)",
        report_path,
        len(modules),
        len(subsystems),
        len(interfaces),
    )
    return report_path


__all__ = ["build_report"]
