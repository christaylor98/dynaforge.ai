"""Focus management for iterative discovery runs."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Mapping, Optional


DEFAULT_FOCUS_NOTES = Path(".codexa/discovery/focus_notes.md")
FOCUS_CONTEXT_PATH = Path(".codexa/discovery/focus_context.json")


@dataclass
class FocusContext:
    user_notes: str
    auto_focus: List[str]
    generated_at: str

    def to_dict(self) -> Mapping[str, object]:
        return asdict(self)


def load_user_focus(source: Optional[str | Path] = None) -> str:
    candidate: Optional[Path]
    if source is None:
        candidate = DEFAULT_FOCUS_NOTES
    else:
        resolved = Path(source)
        candidate = resolved if resolved.exists() else None
    if candidate and candidate.exists():
        return candidate.read_text(encoding="utf-8")
    if isinstance(source, str) and source and not Path(source).exists():
        # Treat raw string as inline focus text
        return source
    return ""


def derive_auto_focus(
    manifest: Optional[Mapping[str, object]],
    *,
    threshold: float = 0.75,
    limit: int = 8,
) -> List[str]:
    if not manifest:
        return []
    modules: Iterable[Mapping[str, object]] = manifest.get("modules") or []
    low_conf = [
        entry.get("file")
        for entry in modules
        if isinstance(entry, Mapping)
        and isinstance(entry.get("file"), str)
        and isinstance(entry.get("confidence"), (int, float))
        and entry["confidence"] < threshold
    ]
    return list(dict.fromkeys(low_conf))[:limit]


def write_focus_context(
    user_notes: str,
    auto_focus: Iterable[str],
    *,
    output_path: Path = FOCUS_CONTEXT_PATH,
) -> None:
    payload = FocusContext(
        user_notes=user_notes,
        auto_focus=list(auto_focus),
        generated_at=datetime.utcnow().isoformat(),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload.to_dict(), indent=2), encoding="utf-8")


def load_focus_context(path: Path = FOCUS_CONTEXT_PATH) -> Optional[FocusContext]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    try:
        return FocusContext(
            user_notes=str(data.get("user_notes", "")),
            auto_focus=list(data.get("auto_focus") or []),
            generated_at=str(data.get("generated_at") or ""),
        )
    except (TypeError, ValueError):
        return None


__all__ = [
    "FocusContext",
    "DEFAULT_FOCUS_NOTES",
    "FOCUS_CONTEXT_PATH",
    "load_user_focus",
    "derive_auto_focus",
    "write_focus_context",
    "load_focus_context",
]
