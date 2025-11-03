from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

from codexa.discovery.analyzers import build_repository_insights


class RepositoryAnalyzerTest(unittest.TestCase):
    def test_python_insight_reports_functions_and_classes(self) -> None:
        module = Path.cwd() / "tests" / "__tmp_discovery_analyzer.py"
        module.write_text(
            textwrap.dedent(
                """
                class Demo:
                    def method(self):
                        value = 0
                        for i in range(3):
                            value += i
                        return value

                def helper():
                    return Demo()
                """
            ),
            encoding="utf-8",
        )

        try:
            file_index = [
                {
                    "path": str(module.relative_to(Path.cwd())),
                    "zone": "analysis",
                    "language": "python",
                    "bytes": module.stat().st_size,
                }
            ]

            insights = build_repository_insights(file_index)
        finally:
            module.unlink(missing_ok=True)

        self.assertEqual(len(insights), 1)
        info = insights[0]
        self.assertEqual(sorted(info["functions"]), ["helper", "method"])
        self.assertIn("Demo", info["classes"])
        self.assertGreater(info["complexity"], 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
