"""AST-backed source analysis for Codexa discovery.

This module provides a lightweight intermediate representation (IR) that is
consumed by the adaptive discovery pipeline.  The initial implementation
focuses on Python sources so the pipeline can begin exercising the model
routing flow immediately; support for additional languages can be layered in
by wiring in Tree-sitter or language specific front-ends later.
"""

from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional


SUPPORTED_SUFFIXES = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cs": "csharp",
}

AST_CACHE_DIR = Path(".codexa/discovery/cache/ast")


@dataclass
class ComplexitySnapshot:
    """Structural metrics extracted from source analysis."""

    loc: int
    function_count: int
    class_count: int
    import_count: int
    avg_block_size: float
    docstring_density: float


@dataclass
class ModuleIR:
    """Intermediate representation describing a single module."""

    file: str
    language: str
    functions: List[str]
    classes: List[str]
    imports: List[str]
    complexity: ComplexitySnapshot
    docstrings: Dict[str, str]
    ast_hash: str

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["complexity"] = asdict(self.complexity)
        return payload


def detect_language(path: Path) -> Optional[str]:
    return SUPPORTED_SUFFIXES.get(path.suffix.lower())


def _ensure_cache_dir() -> None:
    AST_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(path: Path) -> Path:
    key = hashlib.sha256(str(path).encode("utf-8")).hexdigest()
    return AST_CACHE_DIR / f"{key}.json"


def _load_cached_ir(path: Path, content_hash: str) -> Optional[ModuleIR]:
    cache_file = _cache_path(path)
    if not cache_file.exists():
        return None
    try:
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if payload.get("content_hash") != content_hash:
        return None
    data = payload.get("data")
    if not isinstance(data, Mapping):
        return None
    try:
        complexity = ComplexitySnapshot(**data.get("complexity", {}))
        return ModuleIR(
            file=str(data.get("file", "")),
            language=str(data.get("language", "")),
            functions=list(data.get("functions") or []),
            classes=list(data.get("classes") or []),
            imports=list(data.get("imports") or []),
            complexity=complexity,
            docstrings=dict(data.get("docstrings") or {}),
            ast_hash=str(data.get("ast_hash", "")),
        )
    except TypeError:
        return None


def _store_cached_ir(path: Path, content_hash: str, module: ModuleIR) -> None:
    _ensure_cache_dir()
    cache_file = _cache_path(path)
    payload = {
        "content_hash": content_hash,
        "data": module.to_dict(),
    }
    cache_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class _PythonAnalyzer(ast.NodeVisitor):
    """Collect symbol information and structural metrics for Python sources."""

    def __init__(self) -> None:
        self.functions: List[str] = []
        self.classes: List[str] = []
        self.imports: List[str] = []
        self.docstrings: Dict[str, str] = {}
        self._total_block_size = 0
        self._block_count = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self.functions.append(node.name)
        doc = ast.get_docstring(node)
        if doc:
            self.docstrings[f"function:{node.name}"] = doc
        self._register_block(node.body)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        self.classes.append(node.name)
        doc = ast.get_docstring(node)
        if doc:
            self.docstrings[f"class:{node.name}"] = doc
        self._register_block(node.body)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        for alias in node.names:
            self.imports.append(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        module = node.module or ""
        for alias in node.names:
            target = f"{module}.{alias.name}" if module else alias.name
            self.imports.append(target)

    def _register_block(self, body: List[ast.stmt]) -> None:
        self._total_block_size += max(len(body), 1)
        self._block_count += 1

    def average_block_size(self) -> float:
        if self._block_count == 0:
            return 0.0
        return self._total_block_size / self._block_count


def _stable_hash(payload: Dict[str, object]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def analyse_python(path: Path, source: str) -> ModuleIR:
    tree = ast.parse(source, filename=str(path))
    analyzer = _PythonAnalyzer()
    analyzer.visit(tree)

    loc = source.count("\n") + 1 if source else 0
    docstring_count = len(analyzer.docstrings)
    function_count = len(analyzer.functions)
    class_count = len(analyzer.classes)
    import_count = len(analyzer.imports)
    docstring_density = docstring_count / max(function_count + class_count, 1)

    complexity = ComplexitySnapshot(
        loc=loc,
        function_count=function_count,
        class_count=class_count,
        import_count=import_count,
        avg_block_size=round(analyzer.average_block_size(), 3),
        docstring_density=round(docstring_density, 3),
    )

    payload = {
        "file": str(path),
        "language": "python",
        "functions": sorted(analyzer.functions),
        "classes": sorted(analyzer.classes),
        "imports": sorted(set(analyzer.imports)),
        "docstrings": analyzer.docstrings,
        "complexity": asdict(complexity),
    }

    return ModuleIR(
        file=str(path),
        language="python",
        functions=sorted(analyzer.functions),
        classes=sorted(analyzer.classes),
        imports=sorted(set(analyzer.imports)),
        complexity=complexity,
        docstrings=analyzer.docstrings,
        ast_hash=_stable_hash(payload),
    )


def analyse_generic(path: Path, source: str, language: str) -> ModuleIR:
    loc = source.count("\n") + 1 if source else 0
    imports = _guess_imports(source, language)
    complexity = ComplexitySnapshot(
        loc=loc,
        function_count=0,
        class_count=0,
        import_count=len(imports),
        avg_block_size=0.0,
        docstring_density=0.0,
    )
    payload = {
        "file": str(path),
        "language": language,
        "functions": [],
        "classes": [],
        "imports": imports,
        "docstrings": {},
        "complexity": asdict(complexity),
    }
    return ModuleIR(
        file=str(path),
        language=language,
        functions=[],
        classes=[],
        imports=imports,
        complexity=complexity,
        docstrings={},
        ast_hash=_stable_hash(payload),
    )


def parse_file(path: Path) -> Optional[ModuleIR]:
    language = detect_language(path)
    if language is None:
        return None
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    content_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
    cached = _load_cached_ir(path, content_hash)
    if cached:
        return cached
    if language == "python":
        try:
            module = analyse_python(path, source)
        except SyntaxError:
            module = analyse_generic(path, source, language)
    else:
        module = analyse_generic(path, source, language)
    _store_cached_ir(path, content_hash, module)
    return module


def _guess_imports(source: str, language: str) -> List[str]:
    imports: List[str] = []
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if language in {"javascript", "typescript"} and stripped.startswith("import "):
            token = stripped.split()[1]
            imports.append(token.rstrip(";"))
        elif language in {"c", "cpp"} and stripped.startswith("#include"):
            token = stripped.split(maxsplit=1)[-1]
            imports.append(token.strip("<>\""))
        elif language == "csharp" and stripped.startswith("using "):
            token = stripped.split()[1].rstrip(";")
            imports.append(token)
        elif language == "go" and stripped.startswith("import"):
            parts = stripped.split()
            if len(parts) > 1:
                imports.append(parts[-1].strip('"'))
        elif language == "java" and stripped.startswith("import "):
            token = stripped.split()[1].rstrip(";")
            imports.append(token)
    return sorted({imp for imp in imports if imp})


def parse_repository(root: Path) -> Iterator[ModuleIR]:
    root = root.expanduser().resolve()
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if detect_language(file_path) is None:
            continue
        relative = file_path.relative_to(root)
        module = parse_file(file_path)
        if module:
            module.file = str(relative)
            yield module


def load_or_analyse(paths: Iterable[Path]) -> List[ModuleIR]:
    modules: List[ModuleIR] = []
    for path in paths:
        module = parse_file(path)
        if module:
            modules.append(module)
    return modules


__all__ = [
    "ComplexitySnapshot",
    "ModuleIR",
    "detect_language",
    "parse_file",
    "parse_repository",
    "load_or_analyse",
]
