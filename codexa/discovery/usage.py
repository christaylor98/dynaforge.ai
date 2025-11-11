"""Usage tracking for discovery model invocations."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


def log_usage(
    project_root: Path,
    *,
    model: str,
    stage: str,
    prompt_chars: int,
    response_chars: int,
    cached: bool,
    extra: Mapping[str, Any] | None = None,
) -> None:
    """Append a usage record to `.codexa/discovery/usage.log`."""

    project_root = project_root.expanduser().resolve()
    log_path = project_root / ".codexa" / "discovery" / "usage.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    record: dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": model,
        "stage": stage,
        "prompt_chars": prompt_chars,
        "response_chars": response_chars,
        "cached": cached,
    }
    if extra:
        record.update(extra)

    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


__all__ = ["log_usage"]
