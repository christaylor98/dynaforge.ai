from __future__ import annotations

from pathlib import Path

from codexa.reporting import generate_markdown_report


def test_generate_markdown_report_writes_markdown(tmp_path: Path) -> None:
    manifest_dir = tmp_path / ".codexa" / "manifest"
    manifest_dir.mkdir(parents=True)
    manifolds = tmp_path / ".codexa" / "manifests"
    manifolds.mkdir(parents=True)

    (manifest_dir / "domains.json").write_text(
        """{"domains": [{"path": "typer", "kind": "code", "file_count": 10, "languages": {"python": 10}, "description": "Typer package"}]}""",
        encoding="utf-8",
    )
    (manifest_dir / "requirements").mkdir()
    (manifest_dir / "requirements" / "FR-01.json").write_text(
        """{"id": "FR-01", "title": "Baseline understanding", "domain": "typer", "summary": "Typer package"}""",
        encoding="utf-8",
    )
    (manifolds / "system_manifest.yaml").write_text(
        """
summary:
  project_phase: Discovery
  understanding_metrics:
    coverage_percent: 88.2
    discovery_freshness: '2025-11-05T00:00:00Z'
architecture:
  layers:
    - name: Core Framework
      responsibilities:
        - Provide CLI primitives
      components:
        - path: typer/core.py
""",
        encoding="utf-8",
    )

    report_path = generate_markdown_report(tmp_path)
    content = report_path.read_text(encoding="utf-8")

    assert "Codexa Discovery Report" in content
    assert "Typer package" in content
    assert "FR-01" in content
