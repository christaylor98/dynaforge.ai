from __future__ import annotations

import io
from pathlib import Path
from unittest import mock

import pytest

from codexa import cli, config_tools


def _create_sample_project(root: Path) -> None:
    (root / "src").mkdir()
    (root / "src" / "main.py").write_text("print('hello world')\n", encoding="utf-8")
    (root / "node_modules").mkdir()
    (root / ".git").mkdir()
    (root / "README.md").write_text("# Sample\n", encoding="utf-8")


def test_generate_config_recommendation_detects_python(tmp_path: Path) -> None:
    _create_sample_project(tmp_path)

    report = config_tools.generate_config_recommendation(tmp_path)
    config = report["config"]

    assert "src/**" in config["run"]["focus"]
    assert "node_modules/" in config["run"]["skip_paths"]
    assert any(entry["language"] == "python" for entry in report["summary"]["language_sample"])
    outputs = config["outputs"]
    assert outputs["manifest_path"].startswith(".codexa/")
    assert outputs["metrics_path"].startswith(".codexa/")

    config_path = tmp_path / ".codexa" / "config.yaml"
    written = config_tools.write_config_yaml(report["yaml"], config_path)
    assert written.exists()

    with pytest.raises(FileExistsError):
        config_tools.write_config_yaml(report["yaml"], config_path)


def test_cli_init_auto_config_writes_file(tmp_path: Path) -> None:
    _create_sample_project(tmp_path)

    buf = io.StringIO()
    with mock.patch("sys.stdout", buf):
        cli.main(
            [
                "init",
                "--auto-config",
                "--write-config",
                "--root",
                str(tmp_path),
                "--force",
            ]
        )

    output = buf.getvalue()
    assert "Auto-configuration recommendation" in output

    config_path = tmp_path / ".codexa" / "config.yaml"
    assert config_path.exists()
    content = config_path.read_text(encoding="utf-8")
    assert "generator: codexa init --auto-config" in content
