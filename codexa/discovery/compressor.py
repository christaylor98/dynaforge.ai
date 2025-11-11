"""AST IR compressor for token-efficient summarisation."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from hashlib import sha1
from pathlib import Path
from typing import Any, Dict, Iterable, List


@dataclass
class SymbolDigest:
    file: str
    language: str
    functions: List[str]
    classes: List[str]
    imports: List[str]
    metrics: Dict[str, Any]
    ast_hash: str | None
    digest_hash: str


def make_symbol_digest(file_ir: Dict[str, Any]) -> SymbolDigest:
    complexity = file_ir.get("complexity", {})
    compact_metrics = {
        "loc": complexity.get("loc", 0),
        "fc": complexity.get("function_count", 0),
        "cc": complexity.get("class_count", 0),
        "ic": complexity.get("import_count", 0),
        "cd": round(complexity.get("comment_density", 0.0), 3),
    }

    functions = list(file_ir.get("functions") or [])[:10]
    classes = list(file_ir.get("classes") or [])[:5]
    imports = list(file_ir.get("imports") or [])[:10]

    payload = {
        "F": file_ir.get("file", ""),
        "L": file_ir.get("language", ""),
        "CLS": classes,
        "FNS": functions,
        "IMPS": imports,
        "MET": compact_metrics,
    }
    digest_text = json.dumps(payload, separators=(",", ":"))
    digest_hash = sha1(digest_text.encode("utf-8")).hexdigest()[:10]

    return SymbolDigest(
        file=file_ir.get("file", ""),
        language=file_ir.get("language", ""),
        functions=functions,
        classes=classes,
        imports=imports,
        metrics=compact_metrics,
        ast_hash=file_ir.get("ast_hash"),
        digest_hash=digest_hash,
    )


def compress_directory(file_irs: Iterable[Dict[str, Any]]) -> List[SymbolDigest]:
    return [make_symbol_digest(ir) for ir in file_irs]


def save_symbol_digests(
    digests: Iterable[SymbolDigest],
    out_path: Path = Path(".codexa/discovery/cache/symbol_digests.jsonl"),
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for digest in digests:
            handle.write(json.dumps(asdict(digest), separators=(",", ":")) + "\n")


def digest_to_prompt(d: SymbolDigest) -> str:
    m = d.metrics
    return (
        f"F:{d.file} | L:{d.language} | C:{','.join(d.classes)} | "
        f"Fns:{','.join(d.functions)} | Imps:{','.join(d.imports)} | "
        f"Met:loc{m['loc']},fc{m['fc']},cc{m['cc']},ic{m['ic']},cd{m['cd']}"
    )


__all__ = [
    "SymbolDigest",
    "make_symbol_digest",
    "compress_directory",
    "save_symbol_digests",
    "digest_to_prompt",
]
