"""Repository analyzers used by `codexa discover`."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


@dataclass
class FileInsight:
    path: str
    language: str
    bytes: int
    functions: list[str]
    classes: list[str]
    complexity: int

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "language": self.language,
            "bytes": self.bytes,
            "functions": self.functions,
            "classes": self.classes,
            "complexity": self.complexity,
        }


class RepositoryAnalyzer:
    """Run lightweight structural analysis for supported languages."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or Path.cwd()).resolve()

    def analyse(self, file_index: Iterable[Mapping[str, object]]) -> list[FileInsight]:
        insights: list[FileInsight] = []
        for entry in file_index:
            language = entry.get("language")
            path = entry.get("path")
            size = int(entry.get("bytes", 0))
            if not isinstance(path, str):
                continue
            if language == "python":
                insight = self._analyse_python(Path(path), size)
            else:
                insight = FileInsight(
                    path=path,
                    language=str(language or "unknown"),
                    bytes=size,
                    functions=[],
                    classes=[],
                    complexity=0,
                )
            insights.append(insight)
        return insights

    def _analyse_python(self, relative_path: Path, size: int) -> FileInsight:
        abs_path = self.root / relative_path
        try:
            source = abs_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return FileInsight(
                path=str(relative_path),
                language="python",
                bytes=size,
                functions=[],
                classes=[],
                complexity=0,
            )

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return FileInsight(
                path=str(relative_path),
                language="python",
                bytes=size,
                functions=[],
                classes=[],
                complexity=0,
            )

        functions: list[str] = []
        classes: list[str] = []
        complexity = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                complexity += max(1, len(node.body))
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(node.name)
                complexity += max(1, len(node.body))
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
                complexity += max(1, len(node.body))

        return FileInsight(
            path=str(relative_path),
            language="python",
            bytes=size,
            functions=sorted(functions),
            classes=sorted(classes),
            complexity=complexity,
        )


def build_repository_insights(
    file_index: Iterable[Mapping[str, object]],
    *,
    root: Path | None = None,
) -> list[dict[str, object]]:
    analyzer = RepositoryAnalyzer(root=root)
    return [insight.to_dict() for insight in analyzer.analyse(file_index)]
