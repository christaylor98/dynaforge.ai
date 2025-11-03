#!/usr/bin/env python3
"""
Populate MS-02 storyboard artifacts with sample data to simulate a dry run.

Usage examples:
    python3 scripts/ms02_dry_run.py \
        --scope-type change \
        --scope-id CH-010 \
        --requirements REQ-0101,REQ-0102 \
        --discovery-mode full \
        --coverage 0.72 \
        --followups issue-12,issue-14

If no arguments are supplied, sensible defaults matching the storyboard are used.
Existing artifact files are recreated deterministically.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ITERATION_LOG_PATH = ROOT / "docs/status/iteration_log.md"
LOOP_PLAN_PATH = ROOT / "loop-plan.json"
SUMMARY_PATH = ROOT / "artifacts/ms02/storyboard/summary.md"
GAPS_PATH = ROOT / "artifacts/ms02/storyboard/gaps.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-type", choices=["requirement", "change", "phase", "milestone"],
                        default="change", help="Execution scope selected during loop planning.")
    parser.add_argument("--scope-id", default="CH-010", help="Identifier for the selected scope.")
    parser.add_argument("--description", default="Modernise billing pipeline",
                        help="Human-readable description of the scope.")
    parser.add_argument("--requirements", default="REQ-0101,REQ-0102",
                        help="Comma-separated list of curated requirement IDs.")
    parser.add_argument("--discovery-mode", default="full",
                        help="Discovery mode used during the dry run.")
    parser.add_argument("--coverage", type=float, default=0.68,
                        help="Understanding coverage percentage (0-1 range).")
    parser.add_argument("--followups", default="",
                        help="Comma-separated list of outstanding follow-up IDs.")
    parser.add_argument("--iteration", type=int, default=1,
                        help="Iteration number to record in the log.")
    return parser


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_iteration_log(args: argparse.Namespace) -> None:
    followups = [f.strip() for f in args.followups.split(",") if f.strip()]
    followup_cell = ", ".join(followups) if followups else "—"
    coverage_pct = f"{args.coverage * 100:.1f}%"
    table = [
        "# Discovery Iteration Log",
        "",
        "| Iteration | Trigger | Key Findings | Follow-ups (IDs) | Human Notes | Status |",
        "| --- | --- | --- | --- | --- | --- |",
        f"| {args.iteration} | `codexa discover --config docs/discovery/config.yaml` "
        f"(mode={args.discovery_mode}) | Coverage {coverage_pct} — scope highlights captured "
        f"in `summary.md` | {followup_cell} | _Add notes here_ | open |",
        "",
        "## Usage",
        "- This table is updated by the Discovery Analyzer and Project Manager after each "
        "`codexa discover` run.",
        "- Follow-up IDs map to conversational prompts (e.g., “accept follow-up issue-12”) "
        "and to entries in `artifacts/ms02/storyboard/gaps.md` when applicable.",
        "- Humans can append free-form notes in the “Human Notes” column or add commentary beneath "
        "the table; the AI will reconcile these notes into the summary row on the next update.",
        "",
        "## Manual Notes",
        "- _Add any overarching comments, waivers, or scheduling decisions here. The AI preserves "
        "this section verbatim._",
        "",
    ]
    ITERATION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ITERATION_LOG_PATH.write_text("\n".join(table), encoding="utf-8")


def write_loop_plan(args: argparse.Namespace) -> None:
    payload = {
        "scope": {
            "type": args.scope_type,
            "id": args.scope_id,
            "description": args.description,
        },
        "source": {
            "requested_by": "human.pm",
            "prompt": f"Let's run {args.scope_id} next.",
            "captured_at": now_iso(),
        },
        "artifacts": {
            "requirements": [req.strip() for req in args.requirements.split(",") if req.strip()],
            "discovery_manifests": [
                "analysis/system_manifest.yaml",
                "analysis/change_zones.md",
                "analysis/intent_map.md",
            ],
        },
        "notes": [
            "Seed Planner will generate bundle via `codexa seed --from loop-plan`.",
            "Update before execution to reflect actual scope/handoff context.",
        ],
    }
    LOOP_PLAN_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_summary(args: argparse.Namespace) -> None:
    coverage_pct = f"{args.coverage * 100:.1f}%"
    followups = [f.strip() for f in args.followups.split(",") if f.strip()]
    followup_list = ", ".join(followups) if followups else "None"
    summary = [
        "# MS-02 Governance Summary",
        "",
        f"- **Loop Plan Scope:** {args.scope_type.upper()} — {args.scope_id}",
        f"- **Discovery Inputs:** `analysis/system_manifest.yaml` (mode={args.discovery_mode}), "
        "`analysis/change_zones.md`, `analysis/intent_map.md`",
        "- **Execution Bundle:** `changes/CH-###/seed/`",
        "",
        "## Highlights",
        f"- Understanding coverage at {coverage_pct}; scope `{args.scope_id}` prepared for execution.",
        "- Conversational reviews captured design/test approvals; any additional notes belong below.",
        "",
        "## Metrics Snapshot",
        "| Metric | Value | Source |",
        "| --- | --- | --- |",
        f"| Understanding Coverage | {coverage_pct} | `analysis/metrics/understanding_coverage.yaml` |",
        f"| Discovery Freshness | {now_iso()} | `analysis/system_manifest.yaml` metadata |",
        f"| Outstanding Follow-ups | {followup_list} | `docs/status/iteration_log.md` |",
        "",
        "## Decisions",
        "- Pending human confirmation to publish governance report (dry-run sample).",
        "",
        "---",
        "_Generated via `scripts/ms02_dry_run.py`. Replace or append details as the real run progresses._",
        "",
    ]
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text("\n".join(summary), encoding="utf-8")


def write_gaps(args: argparse.Namespace) -> None:
    followups = [f.strip() for f in args.followups.split(",") if f.strip()]
    rows = []
    for idx, fid in enumerate(followups, start=1):
        rows.append(
            f"| gap-{idx:03d} | Resolve follow-up `{fid}` | PM | "
            "AI to confirm resolution via follow-up prompts | open |"
        )
    if not rows:
        rows.append("| gap-000 | None | — | — | closed |")

    content = [
        "# MS-02 Governance Gaps",
        "",
        "| ID | Description | Owner | Proposed Action | Status |",
        "| --- | --- | --- | --- | --- |",
        *rows,
        "",
        "## Notes",
        "- This file is generated during storyboard dry runs. Update owners/actions in plain language; "
        "the orchestrator reconciles changes on the next summary cycle.",
        "",
    ]
    GAPS_PATH.write_text("\n".join(content), encoding="utf-8")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    write_iteration_log(args)
    write_loop_plan(args)
    write_summary(args)
    write_gaps(args)

    print("MS-02 dry run artifacts refreshed:")
    for path in (ITERATION_LOG_PATH, LOOP_PLAN_PATH, SUMMARY_PATH, GAPS_PATH):
        print(f" - {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
