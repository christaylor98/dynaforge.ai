"""
Codexa command-line interface.

Currently implements the `codexa discover` command which drives the
discovery workflow, computes blast-radius recommendations, and updates
history/audit artifacts.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Optional

from scripts import discovery_bootstrap
from . import config_tools, status as status_tools
from .reporting import generate_markdown_report
from .manifest_builder import describe_project
from .discovery import DiscoveryContext, DiscoveryPipeline, build_default_registry, load_focus_context


def _render_text_summary(
    result: Dict[str, Any],
    *,
    project_root: Path,
    config_path: Path,
) -> str:
    """Return a human-readable summary for text output."""
    rel_config = (
        str(config_path.relative_to(project_root))
        if config_path.is_relative_to(project_root)
        else str(config_path)
    )

    emoji = {
        "manifest": "📘",
        "change_zones": "🧭",
        "intent_map": "🕸️",
        "metrics": "📊",
    }

    lines = [
        f"🗂️  Config: {rel_config}",
        "📦 Artifacts:",
    ]
    for label, path in result["paths"].items():
        marker = emoji.get(label, "•")
        lines.append(f"  {marker} {label}: {path}")

    radius = result.get("blast_radius", {})
    changed_zones = radius.get("changed_zones") or []
    removed_zones = radius.get("removed_zones") or []
    recommended_agents = radius.get("recommended_agents") or []

    lines.append(
        f"🚨 Blast radius: {radius.get('level', 'unknown')} "
        f"(zones: {', '.join(changed_zones) if changed_zones else 'none'})"
    )
    if removed_zones:
        lines.append(f"  ⛔ Zones removed: {', '.join(removed_zones)}")
    if recommended_agents:
        lines.append(f"  🤖 Recommended agents: {', '.join(recommended_agents)}")
    notes = radius.get("notes") or []
    for note in notes:
        lines.append(f"- {note}")

    coverage = result.get("coverage", {})
    coverage_percent = coverage.get("coverage_percent")
    if coverage_percent is not None:
        lines.append(f"📈 Coverage: {coverage_percent:.1f}%")

    insights = result.get("insights") or []
    domains = result.get("inferred_domains") or []
    if domains:
        summary = describe_project(domains)
        if summary:
            lines.append(summary)
        lines.append("🌐 Inferred domains:")
        for domain in domains[:4]:
            desc = domain.get("description") or ""
            note = f" — {desc}" if desc else ""
            lines.append(
                f"  • {domain['path']}: {domain['kind']} ({domain['file_count']} files){note}"
            )

    if insights:
        language_counts: Counter[str] = Counter()
        zone_counts: Counter[str] = Counter()
        for insight in insights:
            language = insight.get("language")
            if isinstance(language, str):
                language_counts[language] += 1
            path = insight.get("path")
            if isinstance(path, str) and path:
                zone = path.split("/", 1)[0]
                zone_counts[zone] += 1

        total_files = len(insights)
        top_languages = ", ".join(
            f"{lang} ({count})" for lang, count in language_counts.most_common(3)
        )
        top_zones = ", ".join(
            f"{zone} ({count})" for zone, count in zone_counts.most_common(3)
        )
        lines.append(
            f"🧮 Indexed {total_files} files across {len(zone_counts) or 1} zones"
        )
        if top_languages:
            lines.append(f"  🗣️ Languages: {top_languages}")
        if top_zones:
            lines.append(f"  🧭 Zones: {top_zones}")

    notes = radius.get("notes") or []
    for note in notes:
        lines.append(f"📝 Note: {note}")

    if not insights:
        lines.append("⚠️  Snapshot indexed no files — check focus filters.")

    lines.append("✨ Next steps:")
    lines.append("  • Run `codexa report` to generate .codexa/reports/discovery_report.md")

    return "\n".join(lines)


def _emit_recommendation_summary(recommendation: Dict[str, Any]) -> None:
    summary = recommendation["summary"]
    print(
        "[bootstrap] No discovery config found; generating a starter config for "
        f"{summary['project_root']}."
    )
    languages = summary.get("language_sample") or []
    if languages:
        language_text = ", ".join(
            f"{entry['language']} ({entry['files']})" for entry in languages
        )
        print(f"  Languages detected: {language_text}")
    skip_suggestions = summary.get("skip_suggestions") or []
    if skip_suggestions:
        print("  Skip paths: " + ", ".join(skip_suggestions))
    focus_suggestions = summary.get("focus_suggestions") or []
    if focus_suggestions:
        print("  Focus patterns: " + ", ".join(focus_suggestions))
    print("\nSuggested config.yaml:\n")
    print(recommendation["yaml"])


def _resolve_or_bootstrap_config(
    project_root: Path,
    config_arg: Optional[Path],
) -> Path:
    project_root = project_root.expanduser().resolve()
    search_order: list[Path] = []
    if config_arg:
        candidate = config_arg if config_arg.is_absolute() else project_root / config_arg
        search_order.append(candidate)
    codexa_default = project_root / ".codexa" / "config.yaml"
    docs_default = project_root / "docs" / "discovery" / "config.yaml"
    for candidate in (codexa_default, docs_default):
        if candidate not in search_order:
            search_order.append(candidate)

    for candidate in search_order:
        if candidate.exists():
            return candidate

    recommendation = config_tools.generate_config_recommendation(project_root)
    _emit_recommendation_summary(recommendation)

    target_path = search_order[0] if search_order else codexa_default
    written = config_tools.write_config_yaml(recommendation["yaml"], target_path)
    print(f"[bootstrap] Saved discovery config to {written}")
    return written


def discover_command(args: argparse.Namespace) -> int:
    project_root = Path(args.project).expanduser().resolve() if args.project else Path.cwd()
    config_path = _resolve_or_bootstrap_config(project_root, args.config)

    result = discovery_bootstrap.run_discovery(
        config_path=config_path,
        mode_override=args.mode,
        log_handoff=args.log_handoff,
        track_history=not args.no_history,
        project_root=project_root,
    )

    print(
        _render_text_summary(
            result,
            project_root=project_root,
            config_path=config_path,
        )
    )
    return 0


def discover_next_command(args: argparse.Namespace) -> int:
    project_root = Path(args.project).expanduser().resolve() if args.project else Path.cwd()
    scope = args.scope or None
    focus_source = args.focus if args.focus else args.focus_file

    router_kwargs: Dict[str, object] = {}
    if args.model_policy:
        router_kwargs["policy_mode"] = args.model_policy
    thresholds: Dict[str, float] = {}
    if args.tier1_threshold is not None:
        thresholds["tier1"] = args.tier1_threshold
    if args.tier2_threshold is not None:
        thresholds["tier2"] = args.tier2_threshold
    if thresholds:
        router_kwargs["thresholds"] = thresholds

    prompt_profile = args.prompt_profile or "default"
    adapter_registry = build_default_registry()
    adapter_key = args.model_adapter or "stub"
    summarize_mode = args.summarize_mode
    digest_batch_budget = args.digest_batch_budget
    digest_batch_max = args.digest_batch_max

    if adapter_key == "codex-mcp":
        try:
            from .discovery.adapters.codex_mcp import build_codex_mcp_models
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise SystemExit(
                "Codex MCP adapter requires the `openai-agents` package. Install it with "
                "`pip install openai-agents` before using --model-adapter codex-mcp."
            ) from exc

        adapter_models = build_codex_mcp_models(project_root)
        router_kwargs.setdefault(
            "model_map",
            {"tier1": "codex://gpt-5", "tier2": "codex://gpt-5", "tier3": "codex://gpt-5"},
        )
        if summarize_mode is None:
            summarize_mode = "code"
    elif adapter_key == "gemini":
        try:
            from .discovery.adapters.gemini import build_gemini_models
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise SystemExit(
                "Gemini adapter requires the `google-genai` package. Install it with "
                "`pip install google-genai` before using --model-adapter gemini."
            ) from exc

        adapter_models = build_gemini_models(project_root)
        gemini_model = next(iter(adapter_models.keys()))
        router_kwargs.setdefault(
            "model_map",
            {"tier1": gemini_model, "tier2": gemini_model, "tier3": gemini_model},
        )
        if summarize_mode is None:
            summarize_mode = "digest"
        if digest_batch_budget is None:
            digest_batch_budget = 2000
        if digest_batch_max is None:
            digest_batch_max = 20
    elif adapter_key == "ollama":
        try:
            from .discovery.adapters.ollama import build_ollama_models
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise SystemExit(
                "Ollama adapter requires the `requests` package. Install it with "
                "`pip install requests` before using --model-adapter ollama."
            ) from exc

        adapter_models = build_ollama_models(project_root)
        ollama_model = next(iter(adapter_models.keys()))
        router_kwargs.setdefault(
            "model_map",
            {"tier1": ollama_model, "tier2": ollama_model, "tier3": ollama_model},
        )
        if summarize_mode is None:
            summarize_mode = "digest"
        if digest_batch_budget is None:
            digest_batch_budget = 2000
        if digest_batch_max is None:
            digest_batch_max = 20
    else:
        adapter_config = adapter_registry.get(adapter_key)
        adapter_models = adapter_config.models
        if summarize_mode is None:
            summarize_mode = "code"

    pipeline = DiscoveryPipeline(
        project_root=project_root,
        model_invokers=adapter_models,
        router_kwargs=router_kwargs,
        prompt_profile=prompt_profile,
        summarize_mode=summarize_mode,
        digest_batch_budget=digest_batch_budget,
        digest_batch_max=digest_batch_max,
    )
    context = DiscoveryContext(
        project_root=project_root,
        scope=scope,
        focus_notes=focus_source,
    )
    artifact_path = pipeline.run(context=context, emit_report=not args.no_report)

    manifest_path = project_root / ".codexa/discovery/manifest.json"
    if args.no_report:
        print(f"🔍 Discovery complete. Manifest at {manifest_path}")
    else:
        print(f"📄 Discovery report: {artifact_path}")

    focus_ctx = load_focus_context()
    if focus_ctx:
        if focus_ctx.auto_focus:
            print("🎯 Suggested focus areas for next run:")
            for item in focus_ctx.auto_focus:
                print(f"  - {item}")
        if focus_ctx.user_notes.strip():
            print("📝 User focus notes applied and retained for future runs.")

    return 0


def status_command(args: argparse.Namespace) -> int:
    project_root = Path.cwd()
    report = status_tools.gather_status(project_root)
    print(status_tools.render_status_text(report))
    return 0


def report_command(args: argparse.Namespace) -> int:
    project_root = Path(args.project).expanduser().resolve() if args.project else Path.cwd()
    report_path = generate_markdown_report(project_root)
    print(f"📄 Report generated: {report_path}")
    return 0


def init_command(args: argparse.Namespace) -> int:
    take_action = False

    project_root = (args.root or Path.cwd()).expanduser().resolve()

    if args.operating_model:
        take_action = True
        target_root = project_root / ".codexa"
        report = config_tools.scaffold_operating_model(target_root, force=args.force)
        print(
            f"Operating model scaffold created at {report['root']} "
            f"(directories: {len(report['directories'])}, files: {len(report['files'])})"
        )
        for warning in report.get("warnings", []):
            print(f"[WARN] {warning}")

    if args.auto_config or args.write_config:
        take_action = True
        recommendation = config_tools.generate_config_recommendation(project_root)
        summary = recommendation["summary"]
        print(f"Auto-configuration recommendation for {summary['project_root']}:")
        if summary["language_sample"]:
            language_text = ", ".join(
                f"{entry['language']} ({entry['files']})"
                for entry in summary["language_sample"]
            )
            print(f"  Languages: {language_text}")
        if summary["skip_suggestions"]:
            print(
                "  Skip paths: "
                + ", ".join(summary["skip_suggestions"])
            )
        if summary["focus_suggestions"]:
            print(
                "  Focus patterns: "
                + ", ".join(summary["focus_suggestions"])
            )
        print("\nSuggested config.yaml:\n")
        print(recommendation["yaml"])
        if args.write_config:
            config_path = project_root / ".codexa" / "config.yaml"
            try:
                written = config_tools.write_config_yaml(
                    recommendation["yaml"],
                    config_path,
                    force=args.force,
                )
            except FileExistsError:
                raise SystemExit(
                    f"{config_path} already exists; use --force to overwrite."
                )
            print(f"[saved] {written}")
        else:
            print(
                "\nUse --write-config to persist this recommendation to "
                f"{project_root / '.codexa' / 'config.yaml'}."
            )

    if not take_action:
        raise SystemExit(
            "codexa init requires --operating-model and/or --auto-config."
        )

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
    parser.set_defaults(func=status_command, command=None)
    subparsers = parser.add_subparsers(dest="command", required=False)

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
        "--auto-config",
        action="store_true",
        help="Analyse the project and print a suggested `.codexa/config.yaml`.",
    )
    init_parser.add_argument(
        "--write-config",
        action="store_true",
        help="Persist the suggested config to `.codexa/config.yaml` (overwrites with --force).",
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
        help=argparse.SUPPRESS,
    )
    discover_parser.add_argument(
        "--log-handoff",
        dest="log_handoff",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    discover_parser.add_argument(
        "--no-log-handoff",
        dest="log_handoff",
        action="store_false",
        help=argparse.SUPPRESS,
    )
    discover_parser.set_defaults(log_handoff=None)
    discover_parser.add_argument(
        "--no-history",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    discover_parser.set_defaults(func=discover_command)

    discover_next_parser = subparsers.add_parser(
        "discover-next",
        help="Run the adaptive discovery pipeline (prototype).",
    )
    discover_next_parser.add_argument(
        "--project",
        type=Path,
        help="Project root to analyse (defaults to current directory).",
    )
    discover_next_parser.add_argument(
        "--scope",
        nargs="+",
        help="Optional relative paths/modules to limit discovery.",
    )
    discover_next_parser.add_argument(
        "--focus",
        help="Inline focus notes to prioritise during this run.",
    )
    discover_next_parser.add_argument(
        "--focus-file",
        type=Path,
        help="File containing focus notes or external context to inject.",
    )
    discover_next_parser.add_argument(
        "--model-policy",
        choices=["conservative", "balanced", "aggressive"],
        help="Routing preference: conservative keeps more work on local tier; aggressive promotes quickly.",
    )
    discover_next_parser.add_argument(
        "--model-adapter",
        choices=["stub", "echo", "codex-mcp", "gemini", "ollama"],
        help="Model adapter to use (stub by default).",
    )
    discover_next_parser.add_argument(
        "--summarize-mode",
        choices=["code", "digest"],
        default=None,
        help="Summarization input format (defaults to digest for Gemini, code otherwise).",
    )
    discover_next_parser.add_argument(
        "--digest-batch-budget",
        type=int,
        default=None,
        help="Approximate token budget per digest batch (enabled automatically for Gemini).",
    )
    discover_next_parser.add_argument(
        "--digest-batch-max",
        type=int,
        default=None,
        help="Maximum number of files per digest batch.",
    )
    discover_next_parser.add_argument(
        "--tier1-threshold",
        type=float,
        help="Override base threshold for tier1 (default 0.3).",
    )
    discover_next_parser.add_argument(
        "--tier2-threshold",
        type=float,
        help="Override base threshold for tier2 (default 0.7).",
    )
    discover_next_parser.add_argument(
        "--prompt-profile",
        help="Prompt profile to use (defaults to 'default').",
    )
    discover_next_parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip Markdown report generation (manifest still updated).",
    )
    discover_next_parser.set_defaults(func=discover_next_command)

    report_parser = subparsers.add_parser(
        "report",
        help="Generate a Markdown project discovery summary.",
    )
    report_parser.add_argument(
        "--project",
        type=Path,
        help="Project root to summarise (defaults to current directory).",
    )
    report_parser.set_defaults(func=report_command)

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
