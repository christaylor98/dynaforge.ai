from __future__ import annotations

import io
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import yaml

from codexa import cli, status


def test_gather_status_without_config(tmp_path: Path) -> None:
    report = status.gather_status(tmp_path)
    assert report["config_present"] is False
    assert "Bootstrap discovery" in report["recommendation"]
    assert report["suggested_command"].startswith("codexa discover")


def test_gather_status_with_recent_history(tmp_path: Path) -> None:
    config_path = tmp_path / ".codexa"
    config_path.mkdir()
    (config_path / "config.yaml").write_text("version: 0.1.0\n", encoding="utf-8")

    history_dir = tmp_path / "analysis" / "history"
    history_dir.mkdir(parents=True)
    history_data = [
        {
            "record": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "coverage_percent": 82.3,
                "followups_open": [],
            },
            "blast_radius": {"level": "local", "followups_open": []},
        }
    ]
    (history_dir / "discovery_runs.yaml").write_text(
        yaml.safe_dump(history_data, sort_keys=False), encoding="utf-8"
    )

    report = status.gather_status(tmp_path)
    assert report["config_present"] is True
    assert abs(report["coverage"] - 82.3) < 0.01
    assert report["blast_level"] == "local"
    assert "Discovery looks fresh" in report["recommendation"]


def test_cli_status_default_command(tmp_path: Path) -> None:
    codexa_dir = tmp_path / ".codexa"
    codexa_dir.mkdir()
    (codexa_dir / "config.yaml").write_text("version: 0.1.0\n", encoding="utf-8")

    history_dir = tmp_path / "analysis" / "history"
    history_dir.mkdir(parents=True)
    history_data = [
        {
            "record": {
                "generated_at": (
                    datetime.now(timezone.utc) - timedelta(days=2)
                ).isoformat(),
                "coverage_percent": 70.0,
                "followups_open": [],
            },
            "blast_radius": {"level": "system", "followups_open": []},
        }
    ]
    (history_dir / "discovery_runs.yaml").write_text(
        yaml.safe_dump(history_data, sort_keys=False), encoding="utf-8"
    )

    previous = os.getcwd()
    os.chdir(tmp_path)
    try:
        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            cli.main([])

        output = buf.getvalue()
        assert "Project:" in output
        assert "Recommendation: Discovery snapshot is over 24 hours old" in output
        assert "Suggested command: codexa discover" in output
    finally:
        os.chdir(previous)
