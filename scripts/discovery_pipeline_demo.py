#!/usr/bin/env python3
"""Demonstration entrypoint for the adaptive discovery pipeline.

The script runs the new pipeline using stubbed model invokers so that the
full flow (parse → route → summarise → synthesise → manifest → report) can be
exercised without contacting external model providers.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from codexa.discovery import DiscoveryContext, DiscoveryPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_root",
        nargs="?",
        default=Path.cwd(),
        type=Path,
        help="Project root to analyse.",
    )
    parser.add_argument(
        "--scope",
        nargs="*",
        help="Optional relative paths/directories to limit discovery.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.project_root.expanduser().resolve()
    pipeline = DiscoveryPipeline(project_root=root)
    context = DiscoveryContext(project_root=root, scope=args.scope)
    report_path = pipeline.run(context=context)
    print(f"Discovery pipeline completed. Report available at {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
