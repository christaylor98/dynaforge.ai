#!/usr/bin/env python3
"""Deterministic CLI stub that emulates Discord lifecycle commands."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from audit import log_command

PHASE = "1"

_STATUS_RESPONSE = {
    "command": "/status",
    "phase": PHASE,
    "response_id": "phase1-status-v1",
    "status": "Phase 1 orchestration skeleton generated.",
    "open_concerns": 0,
    "next_checkpoint": "Implement concern lifecycle tooling and capture validation evidence.",
}

_CLARIFY_RESPONSE = {
    "command": "/clarify",
    "phase": PHASE,
    "response_id": "phase1-clarify-v1",
    "guidance": "Phase 1 focuses on concern lifecycle, approvals, and expanded command interfaces.",
    "reference_doc": "docs/PHASE1_PLAN.md",
    "action": "Review WS-101 through WS-108 and prepare status snapshots.",
}


def _emit(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _handle_status(arguments: Sequence[str]) -> dict[str, Any]:
    if arguments:
        raise ValueError("The /status command does not accept arguments.")
    return dict(_STATUS_RESPONSE)


def _handle_clarify(arguments: Sequence[str]) -> dict[str, Any]:
    prompt = " ".join(arguments).strip()
    payload = dict(_CLARIFY_RESPONSE)
    payload["topic"] = prompt or "unspecified"
    return payload


def _handle_ack(arguments: Sequence[str]) -> dict[str, Any]:
    if len(arguments) != 1:
        raise ValueError("The /ack command requires exactly one argument: <concern_id>.")
    concern_id = arguments[0]
    return {
        "command": "/ack",
        "phase": PHASE,
        "response_id": "phase1-ack-v1",
        "concern_id": concern_id,
        "status": "acknowledged",
        "message": f"Concern {concern_id} acknowledged and queued for follow-up.",
    }


def _handle_resolve(arguments: Sequence[str]) -> dict[str, Any]:
    if not arguments:
        raise ValueError("The /resolve command requires at least one argument: <concern_id> [resolution_note].")
    concern_id = arguments[0]
    note = " ".join(arguments[1:]).strip() or "Resolution recorded."
    return {
        "command": "/resolve",
        "phase": PHASE,
        "response_id": "phase1-resolve-v1",
        "concern_id": concern_id,
        "status": "resolved",
        "resolution_note": note,
    }


def _handle_assign(arguments: Sequence[str]) -> dict[str, Any]:
    if len(arguments) < 2:
        raise ValueError("The /assign command requires arguments: <agent> <concern_id>.")
    agent = arguments[0]
    concern_id = arguments[1]
    return {
        "command": "/assign",
        "phase": PHASE,
        "response_id": "phase1-assign-v1",
        "assigned_to": agent,
        "concern_id": concern_id,
        "status": "assigned",
    }


def _handle_pause(arguments: Sequence[str]) -> dict[str, Any]:
    if arguments:
        raise ValueError("The /pause command does not accept arguments.")
    return {
        "command": "/pause",
        "phase": PHASE,
        "response_id": "phase1-pause-v1",
        "status": "paused",
        "message": "Automation paused. Use /resume to continue.",
    }


def _handle_resume(arguments: Sequence[str]) -> dict[str, Any]:
    if arguments:
        raise ValueError("The /resume command does not accept arguments.")
    return {
        "command": "/resume",
        "phase": PHASE,
        "response_id": "phase1-resume-v1",
        "status": "active",
        "message": "Automation resumed. Monitoring concern queue.",
    }


def _handle_promote(arguments: Sequence[str]) -> dict[str, Any]:
    if len(arguments) != 1:
        raise ValueError("The /promote command requires exactly one argument: <target_phase>.")
    target_phase = arguments[0]
    return {
        "command": "/promote",
        "phase": PHASE,
        "response_id": "phase1-promote-v1",
        "target_phase": target_phase,
        "status": "pending_approval",
        "message": f"Promotion request for {target_phase} queued for human approval.",
    }


_COMMAND_HANDLERS: dict[str, Callable[[Sequence[str]], dict[str, Any]]] = {
    "/status": _handle_status,
    "/clarify": _handle_clarify,
    "/ack": _handle_ack,
    "/resolve": _handle_resolve,
    "/assign": _handle_assign,
    "/pause": _handle_pause,
    "/resume": _handle_resume,
    "/promote": _handle_promote,
}


def _build_metadata(response: Mapping[str, Any]) -> dict[str, Any]:
    metadata = {"response_id": response.get("response_id")}
    for key in ("concern_id", "assigned_to", "target_phase", "status"):
        if key in response:
            metadata[key] = response[key]
    return metadata


def main(argv: Sequence[str]) -> int:
    if len(argv) < 2:
        print(
            "Usage: python pipelines/interaction_stub.py "
            "</status|/clarify|/ack|/resolve|/assign|/pause|/resume|/promote> [arguments...]",
            file=sys.stderr,
        )
        return 1

    command = argv[1]
    args = list(argv[2:])
    handler = _COMMAND_HANDLERS.get(command)
    if handler is None:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 2

    try:
        response = handler(args)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    log_command(
        phase=str(response.get("phase", PHASE)),
        issued_by="interaction_stub",
        command=command,
        arguments=args,
        metadata=_build_metadata(response),
    )
    _emit(response)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
