#!/usr/bin/env python3
"""Phase 1 orchestration skeleton with optional run logging."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from agents.designer import Designer
from agents.implementer import Implementer
from agents.project_manager import ProjectManager
from agents.tester import Tester

SCENARIO: Mapping[str, Any] = {
    "phase": "1",
    "title": "Concern Lifecycle Integration",
    "objective": "Implement concern lifecycle mirroring, lifecycle commands, and QA enforcement gates.",
    "context": (
        "Phase 0 established the repository skeleton and logging primitives. "
        "Phase 1 must now operationalize the full agent loop with concern tracking, "
        "human approvals, and policy enforcement."
    ),
    "focus_areas": [
        "Mirror concern entries from JSONL into Markdown summaries.",
        "Extend CLI interaction stub with lifecycle commands (/ack, /resolve, /assign, /pause, /resume, /promote).",
        "Integrate QA policy enforcement prior to promotions.",
        "Provide status snapshots exposing open concerns and QA posture.",
    ],
    "deliverables": [
        "Phase 1 brief, design spec, implementation plan, and QA plan.",
        "`make phase1-demo` executing orchestrated workflow.",
        "Artifacts under `artifacts/phase1/` evidencing the loop.",
    ],
    "success_metrics": [
        "Concern lifecycle documented and observable in Markdown + JSONL.",
        "Interaction stub returns deterministic payloads for lifecycle commands.",
        "QA policy enforcement blocks promotion when thresholds fail.",
    ],
    "acceptance_criteria": [
        "Concern mirroring helper produces deterministic Markdown for docs/PROJECT_DETAIL.md.",
        "Expanded interaction stub logs commands with appropriate metadata.",
        "Tester artifacts describe pass/fail evidence and pending work.",
    ],
}

ARTIFACT_ROOT = Path("artifacts/phase1/orchestration")
SUMMARY_PATH = ARTIFACT_ROOT / "summary.json"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _relative_path(path: Path) -> str:
    path = Path(path)
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def orchestrate() -> dict[str, Any]:
    """Run the phase 1 scenario across the core agents."""
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

    pm = ProjectManager(phase="1")
    brief_path = pm.create_phase_brief(SCENARIO)

    designer = Designer(phase="1")
    design_path = designer.create_design_spec(SCENARIO, brief_path=brief_path)

    implementer = Implementer(phase="1")
    implementation_plan_path = implementer.create_execution_plan(SCENARIO, design_path=design_path)

    tester = Tester(phase="1")
    test_plan_path, test_results_path = tester.prepare_phase_test_assets(SCENARIO)

    summary = {
        "scenario": dict(SCENARIO),
        "artifacts": {
            "brief": _relative_path(brief_path),
            "design_spec": _relative_path(design_path),
            "implementation_plan": _relative_path(implementation_plan_path),
            "test_plan": _relative_path(test_plan_path),
            "test_results": _relative_path(test_results_path),
        },
    }

    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def append_run_log(summary: Mapping[str, Any], log_path: Path) -> None:
    log_path = log_path.expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(summary, indent=2, sort_keys=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"=== Run at {timestamp} ===\n")
        handle.write(f"sha256:{digest}\n")
        handle.write(payload)
        handle.write("\n\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execute the Phase 1 orchestration loop.")
    parser.add_argument(
        "--log",
        type=Path,
        help="Optional path to append run summaries (used for validation evidence).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    summary = orchestrate()
    if args.log:
        append_run_log(summary, args.log)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
