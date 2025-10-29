#!/usr/bin/env python3
"""Deterministic CLI stub that emulates minimal Discord interactions."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Sequence

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from audit import log_command

_STATUS_RESPONSE = {
    "command": "/status",
    "phase": "0",
    "response_id": "phase0-status-v1",
    "status": "Phase 0 scaffolding in progress.",
    "open_concerns": 0,
    "next_checkpoint": "Finalize audit logger validation tests.",
}

_CLARIFY_RESPONSE = {
    "command": "/clarify",
    "phase": "0",
    "response_id": "phase0-clarify-v1",
    "guidance": "Phase 0 targets repository skeleton, logging primitives, and interaction stub.",
    "reference_doc": "docs/PHASE0_PLAN.md",
    "action": "Document outstanding questions in docs/project-qa.md.",
}


def _emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _handle_status(arguments: Sequence[str]) -> dict[str, object]:
    if arguments:
        raise ValueError("The /status command does not accept arguments.")
    return dict(_STATUS_RESPONSE)


def _handle_clarify(arguments: Sequence[str]) -> dict[str, object]:
    prompt = " ".join(arguments).strip()
    payload = dict(_CLARIFY_RESPONSE)
    payload["topic"] = prompt or "unspecified"
    return payload


def main(argv: Sequence[str]) -> int:
    if len(argv) < 2:
        print("Usage: python pipelines/interaction_stub.py </status|/clarify> [arguments...]", file=sys.stderr)
        return 1

    command = argv[1]
    args = list(argv[2:])

    try:
        if command == "/status":
            response = _handle_status(args)
        elif command == "/clarify":
            response = _handle_clarify(args)
        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            return 2
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    log_command(
        phase=str(response["phase"]),
        issued_by="interaction_stub",
        command=command,
        arguments=args,
        metadata={"response_id": response["response_id"]},
    )
    _emit(response)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
