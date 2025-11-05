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

import yaml

REQUIRED_DIRS = ["agents", "rules", "workflows", "manifests", "logs", "state"]
REQUIRED_FILES = ["config.yaml", "README.md"]
GLOBAL_BUNDLE_ROOT = Path.home() / ".config" / "codexa"
AUDIT_LOG = Path("audit") / "doctor_config.jsonl"


class ConfigDoctorError(Exception):
    """Raised when configuration inspection encounters a fatal error."""


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
