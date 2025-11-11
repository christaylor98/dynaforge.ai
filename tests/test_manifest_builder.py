from __future__ import annotations

from pathlib import Path

from codexa.manifest_builder import infer_domains, write_manifest_bundle


def test_infer_domains_classifies_code_and_docs() -> None:
    file_index = [
        {"path": "typer/core.py", "language": "python"},
        {"path": "typer/main.py", "language": "python"},
        {"path": "docs/index.md", "language": "markdown"},
        {"path": "docs/tutorial.md", "language": "markdown"},
        {"path": "tests/test_cli.py", "language": "python"},
    ]

    domains = infer_domains(file_index)
    kinds = {domain.path: domain.kind for domain in domains}
    assert kinds["typer"] == "code"
    assert kinds["docs"] == "docs"
    assert kinds["tests"] == "tests"

    descriptions = {domain.path: domain.description for domain in domains}
    assert "Typer package" in descriptions["typer"]


def test_write_manifest_bundle_outputs_expected_files(tmp_path: Path) -> None:
    file_index = [
        {"path": "typer/core.py", "language": "python"},
        {"path": "docs/index.md", "language": "markdown"},
    ]

    domains = write_manifest_bundle(
        tmp_path,
        file_index=file_index,
        generated_at="2025-11-05T00:00:00Z",
    )

    manifest_root = tmp_path / ".codexa" / "manifest"
    assert (manifest_root / "domains.json").exists()
    assert (manifest_root / "milestones.json").exists()
    assert (manifest_root / "index.json").exists()
    assert (manifest_root / "requirements" / "FR-01.json").exists()
    assert domains
