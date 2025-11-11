"""
Utilities for Codexa operating-model scaffolding and configuration validation.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from collections import Counter

import yaml

REQUIRED_DIRS = ["agents", "rules", "workflows", "manifests", "logs", "state"]
REQUIRED_FILES = ["config.yaml", "README.md"]
GLOBAL_BUNDLE_ROOT = Path.home() / ".config" / "codexa"
AUDIT_LOG = Path("audit") / "doctor_config.jsonl"


class ConfigDoctorError(Exception):
    """Raised when configuration inspection encounters a fatal error."""


class AutoConfigError(Exception):
    """Raised when automatic configuration generation fails."""


def _hash_file(path: Path) -> Optional[str]:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def scaffold_operating_model(root: Path, *, force: bool = False) -> Dict[str, Any]:
    """
    Create the `.codexa/` operating model scaffold at *root*.

    Returns a report dictionary describing actions taken.
    """
    report: Dict[str, Any] = {
        "root": str(root),
        "directories": {},
        "files": {},
        "warnings": [],
    }
    root.mkdir(parents=True, exist_ok=True)

    for directory in REQUIRED_DIRS:
        target = root / directory
        _ensure_directory(target)
        report["directories"][directory] = str(target)

    # Provide .gitkeep files for optional runtime folders
    for optional in ("logs", "state"):
        gitkeep = root / optional / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")

    config_path = root / "config.yaml"
    readme_path = root / "README.md"

    if config_path.exists() and not force:
        report["warnings"].append(
            f"{config_path} already exists; not overwriting (use --force to replace)."
        )
    else:
        config_path.write_text(
            _DEFAULT_CONFIG_TEMPLATE,
            encoding="utf-8",
        )
        report["files"]["config.yaml"] = str(config_path)

    if readme_path.exists() and not force:
        report["warnings"].append(
            f"{readme_path} already exists; not overwriting (use --force to replace)."
        )
    else:
        readme_path.write_text(_DEFAULT_README_CONTENT, encoding="utf-8")
        report["files"]["README.md"] = str(readme_path)

    return report


def _search_for_config_root(start: Path) -> Optional[Path]:
    for candidate in [start, *start.parents]:
        codexa_dir = candidate / ".codexa"
        if codexa_dir.is_dir() and (codexa_dir / "config.yaml").exists():
            return codexa_dir
    return None


def _load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ConfigDoctorError(f"{path} must contain a YAML mapping.")
    return data


def inspect_configuration(
    *,
    config_root: Optional[Path] = None,
    start_path: Optional[Path] = None,
    global_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Inspect the Codexa operating-model configuration.

    Returns a report dictionary containing checks, issues, warnings,
    provenance hashes, and the derived exit code.
    """

    start = (start_path or Path.cwd()).resolve()
    global_dir = (global_root or GLOBAL_BUNDLE_ROOT).expanduser().resolve()
    report: Dict[str, Any] = {
        "timestamp": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "checks": [],
        "issues": [],
        "warnings": [],
        "config_root": None,
        "extends_from": [],
        "template_hashes": {},
        "global_bundle_path": str(global_dir),
    }

    root = (config_root or _search_for_config_root(start))
    if root is not None:
        root = root.expanduser().resolve()

    if root is None:
        report["issues"].append("No `.codexa/` directory with config.yaml found.")
        exit_code = 2
        report["exit_code"] = exit_code
        return report

    report["config_root"] = str(root)

    # Check required files and folders.
    missing_files = [
        req for req in REQUIRED_FILES if not (root / req).is_file()
    ]
    missing_dirs = [
        req for req in REQUIRED_DIRS if not (root / req).is_dir()
    ]

    if missing_files:
        report["issues"].append(
            f"Missing required files: {', '.join(missing_files)}"
        )
    if missing_dirs:
        report["warnings"].append(
            f"Missing recommended directories: {', '.join(missing_dirs)}"
        )

    # Load config.yaml for extends chain.
    config_data = _load_yaml(root / "config.yaml")
    extends = config_data.get("extends") or []
    if isinstance(extends, (str, Path)):
        extends = [str(extends)]
    extends_list: List[str] = []
    if isinstance(extends, Sequence):
        for item in extends:
            extends_list.append(str(item))
    else:
        report["warnings"].append("`extends` is not a list; ignoring.")
    report["extends_from"] = extends_list

    # Verify extends chain existence + hash.
    for entry in extends_list:
        expanded = Path(os.path.expanduser(entry)).resolve()
        if not expanded.exists():
            report["issues"].append(f"Extended config not found: {entry}")
            continue
        hash_value = (
            _hash_file(expanded)
            if expanded.is_file()
            else _hash_file(expanded / "core.yaml")
        )
        if hash_value:
            report["template_hashes"][str(expanded)] = hash_value

    # Hash the project config for provenance.
    project_hash = _hash_file(root / "config.yaml")
    if project_hash:
        report["template_hashes"][str(root / "config.yaml")] = project_hash

    # Check global bundle presence.
    if not global_dir.exists():
        report["warnings"].append(
            f"Global control plane not found at {global_dir}."
        )
    else:
        core_hash = _hash_file(global_dir / "core.yaml")
        if core_hash:
            report["template_hashes"][str(global_dir / "core.yaml")] = core_hash

    # Determine exit code.
    exit_code = 0
    if report["issues"]:
        exit_code = 2
    elif report["warnings"]:
        exit_code = 1
    report["exit_code"] = exit_code
    return report


def render_doctor_text(report: Dict[str, Any]) -> str:
    """Create a human-readable doctor report."""
    lines = [
        f"Configuration root: {report.get('config_root') or 'not found'}",
        f"Global control plane: {report.get('global_bundle_path')}",
    ]

    extends = report.get("extends_from") or []
    if extends:
        lines.append("Extends chain:")
        lines.extend([f"  - {entry}" for entry in extends])
    else:
        lines.append("Extends chain: (none)")

    for key, value in report.get("template_hashes", {}).items():
        lines.append(f"Hash[{key}]: {value}")

    for issue in report.get("issues", []):
        lines.append(f"[ERROR] {issue}")
    for warn in report.get("warnings", []):
        lines.append(f"[WARN] {warn}")

    exit_code = report.get("exit_code", 0)
    status = "OK" if exit_code == 0 else "WARNING" if exit_code == 1 else "ERROR"
    lines.append(f"Overall status: {status} (exit={exit_code})")
    return "\n".join(lines)


def append_doctor_audit(report: Dict[str, Any]) -> None:
    """Append the doctor report to the audit log."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(report, sort_keys=True) + "\n")


AUTO_SKIP_DIRS: Tuple[str, ...] = (
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".idea",
    ".vscode",
    ".DS_Store",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "logs",
    "tmp",
    "temp",
    "venv",
    ".venv",
    ".tox",
    ".ruff_cache",
    ".gitmodules",
    ".terraform",
    "target",
    "out",
    "env",
)

FOCUS_DIR_CANDIDATES: Tuple[str, ...] = (
    "src",
    "app",
    "apps",
    "service",
    "services",
    "backend",
    "frontend",
    "lib",
    "packages",
    "core",
    "server",
    "client",
    "api",
)

LANGUAGE_BY_SUFFIX: Dict[str, str] = {
    ".py": "python",
    ".md": "markdown",
    ".mdx": "markdown",
    ".markdown": "markdown",
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
    ".tsx": "typescript",
    ".rs": "rust",
    ".js": "javascript",
    ".jsx": "javascript",
    ".java": "java",
    ".go": "go",
    ".c": "c",
    ".h": "c-header",
    ".cpp": "cpp",
    ".hpp": "cpp-header",
    ".cs": "csharp",
    ".swift": "swift",
}

MAX_LANGUAGE_SAMPLE = 5000


def _should_skip_during_scan(parts: Tuple[str, ...]) -> bool:
    for part in parts:
        if part in AUTO_SKIP_DIRS:
            return True
        if part.startswith(".") and part not in (".", "..", ".codexa"):
            return True
    return False


def _detect_languages(project_root: Path) -> Counter:
    languages: Counter = Counter()
    files_seen = 0
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(project_root)
        if _should_skip_during_scan(relative.parts):
            continue
        language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower(), "other")
        languages[language] += 1
        files_seen += 1
        if files_seen >= MAX_LANGUAGE_SAMPLE:
            break
    return languages


def _candidate_skip_paths(project_root: Path) -> List[str]:
    skips: List[str] = []
    for entry in project_root.iterdir():
        if not entry.is_dir():
            continue
        name = entry.name
        if name in AUTO_SKIP_DIRS or (name.startswith(".") and name not in (".codexa",)):
            skips.append(f"{name}/")
    return sorted(skips)


def _candidate_focus_paths(project_root: Path, languages: Counter) -> List[str]:
    focus: List[str] = []
    for candidate in FOCUS_DIR_CANDIDATES:
        if (project_root / candidate).is_dir():
            focus.append(f"{candidate}/**")
    for entry in project_root.iterdir():
        if not entry.is_dir():
            continue
        name = entry.name
        if name.startswith('.') or name in AUTO_SKIP_DIRS:
            continue
        if name in FOCUS_DIR_CANDIDATES:
            continue
        package_init = entry / "__init__.py"
        has_python = any(child.suffix == ".py" for child in entry.glob("*.py"))
        if package_init.exists() or has_python:
            focus.append(f"{name}/**")
    if (project_root / "tests").is_dir():
        focus.append("tests/**/*.py")
    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped: List[str] = []
    for pattern in focus:
        if pattern in seen:
            continue
        seen.add(pattern)
        deduped.append(pattern)
    focus = deduped

    if not focus:
        primary_language, *_ = languages.most_common(1) or [(None, 0)]
        if primary_language == "python":
            focus.append("**/*.py")
        elif primary_language == "typescript":
            focus.append("**/*.ts")
        elif primary_language == "javascript":
            focus.append("**/*.js")
    return focus


def _cpu_workers(default: int = 4) -> int:
    cpu_total = os.cpu_count() or default
    return max(2, min(cpu_total, 12))


def generate_config_recommendation(project_root: Path) -> Dict[str, Any]:
    """
    Analyse *project_root* and return a recommendation report containing:
      - summary statistics
      - suggested configuration dictionary
      - rendered YAML text
    """

    project_root = project_root.expanduser().resolve()
    if not project_root.exists():
        raise AutoConfigError(f"{project_root} does not exist.")

    languages = _detect_languages(project_root)
    skip_paths = _candidate_skip_paths(project_root)
    focus_paths = _candidate_focus_paths(project_root, languages)

    language_summary = [
        {"language": language, "files": count}
        for language, count in languages.most_common(5)
    ]
    primary_languages = [
        language
        for language, _ in languages.most_common(3)
        if language and language != "other"
    ]

    summary = {
        "project_root": str(project_root),
        "top_level_dirs": sorted(
            [entry.name for entry in project_root.iterdir() if entry.is_dir()]
        ),
        "language_sample": language_summary,
        "skip_suggestions": skip_paths,
        "focus_suggestions": focus_paths,
    }

    timestamp = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    config: Dict[str, Any] = {
        "metadata": {
            "version": "0.1.0",
            "generated_at": timestamp,
            "generator": "codexa init --auto-config",
        },
        "project": {
            "name": project_root.name or "project",
        },
        "run": {
            "mode": "full",
            "focus": focus_paths,
            "skip_paths": skip_paths,
            "languages": {
                "include": primary_languages,
                "exclude": [],
            },
            "concurrency": {
                "workers": _cpu_workers(),
                "batch_size": 200,
            },
            "telemetry": {
                "enable_progress": True,
                "progress_interval_seconds": 5,
            },
        },
        "outputs": {
        "manifest_path": ".codexa/manifests/system_manifest.yaml",
        "change_zones_path": ".codexa/manifests/change_zones.md",
        "intent_map_path": ".codexa/manifests/intent_map.md",
        "metrics_path": ".codexa/manifests/understanding_coverage.yaml",
        "system_model_refresh": True,
        },
        "audit": {
            "write_handoff": True,
            "log_followups": True,
        },
        "notes": [
            "Review skip/focus suggestions and adjust before committing.",
            "Hand-edit telemetry or audit locations if your repository stores them elsewhere.",
        ],
    }

    yaml_text = yaml.safe_dump(config, sort_keys=False)

    return {
        "summary": summary,
        "config": config,
        "yaml": yaml_text,
    }


def write_config_yaml(
    config_yaml: str,
    target_path: Path,
    *,
    force: bool = False,
) -> Path:
    target_path = target_path.expanduser().resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists() and not force:
        raise FileExistsError(str(target_path))
    target_path.write_text(config_yaml, encoding="utf-8")
    return target_path


_DEFAULT_CONFIG_TEMPLATE = """\
version: 0.1.0
extends:
  - "~/.config/codexa/core.yaml"
project:
  name: "dynaforge.ai"
  milestone: "MS-03"
  maturity: "M2"
discovery:
  manifests_dir: "./manifests"
  default_mode: "quick"
  telemetry:
    enabled: true
    path: "../docs/status/iteration_log.md"
lint:
  enforce_structure: true
  required_files:
    - "config.yaml"
    - "README.md"
"""

_DEFAULT_README_CONTENT = """\
# .codexa/ Operating Model Root

This directory hosts the project-scoped Codexa configuration. All commands
discover this folder first and fall back to the global control plane
(`~/.config/codexa/`) only when necessary.

## Layout
- `config.yaml` — project entry point, may list `extends:` references to shared bundles.
- `agents/` — agent-specific configuration overrides, prompts, or manifests.
- `rules/` — lint, policy, or governance rules that are project-specific.
- `workflows/` — orchestrations and scripts for Codexa CLI invocations.
- `manifests/` — discovery outputs (`system_manifest.yaml`, `change_zones.md`, `intent_map.md`, etc.).
- `logs/` — optional runtime logs emitted by agents/commands (ignored by default).
- `state/` — optional cached state; treated as ephemeral.

## Provenance Logging
`codexa doctor config` computes and records:
- Resolved `config_root`
- `extends_from` chain
- Template hash of the global bundle
- Manifest hash for the latest discovery run

These values appear in audit logs (`audit/*.jsonl`) and status documentation per CR004 / FR-06.

## Migration Notes
Legacy Spec-Kit repositories should run `codexa migrate spec-kit` to populate this
folder. The command performs a dry run by default and documents required
manual follow-ups.
"""
