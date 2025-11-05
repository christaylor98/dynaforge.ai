from __future__ import annotations

import io
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

import yaml

from codexa import cli
from codexa.discovery import BlastRadiusPlanner
from scripts import discovery_bootstrap as db


class DiscoveryWorkflowTest(unittest.TestCase):
    def _fake_scan(self) -> db.ScanResult:
        zone_stats = {
            "analysis": {"file_count": 3, "bytes": 120, "languages": Counter({"python": 3})},
            "audit": {"file_count": 1, "bytes": 30, "languages": Counter({"json": 1})},
        }
        return db.ScanResult(
            language_counts=Counter({"python": 3, "json": 1}),
            zone_stats=zone_stats,
            file_index=[
                {"path": "analysis/module.py", "zone": "analysis", "language": "python", "bytes": 60},
                {"path": "analysis/util.py", "zone": "analysis", "language": "python", "bytes": 60},
                {"path": "audit/log.json", "zone": "audit", "language": "json", "bytes": 30},
            ],
            total_files=4,
            total_bytes=150,
        )

    def test_history_persistence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            config_path = tmp / "docs/discovery/config.yaml"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text("mode: full\n", encoding="utf-8")

            patches = {
                "CONFIG_DEFAULT": config_path,
                "MANIFEST_PATH": tmp / "analysis/system_manifest.yaml",
                "CHANGE_ZONES_PATH": tmp / "analysis/change_zones.md",
                "INTENT_MAP_PATH": tmp / "analysis/intent_map.md",
                "METRICS_PATH": tmp / "analysis/metrics/understanding_coverage.yaml",
                "HANDOFF_LOG_PATH": tmp / "audit/handoff.jsonl",
                "GAPS_PATH": tmp / "artifacts/gaps.md",
                "LOOP_PLAN_PATH": tmp / "loop-plan.json",
                "ITERATION_LOG_PATH": tmp / "docs/status/iteration_log.md",
                "STORYBOARD_SUMMARY_PATH": tmp / "artifacts/summary.md",
                "HISTORY_PATH": tmp / "analysis/history/discovery_runs.yaml",
                "ROOT": tmp,
            }

            with mock.patch.multiple(
                db,
                load_config=mock.MagicMock(return_value={"run": {"mode": "full"}, "audit": {"write_handoff": False}}),
                read_followups=mock.MagicMock(return_value=[]),
                read_gap_followups=mock.MagicMock(return_value=[]),
                read_loop_scope=mock.MagicMock(return_value={"scope": {"id": "CH-123", "type": "change"}}),
                warn_followup_mismatch=mock.MagicMock(),
                scan_repository=mock.MagicMock(return_value=self._fake_scan()),
                git_commit_sha=mock.MagicMock(return_value="deadbeef"),
                now_iso=mock.MagicMock(return_value="2025-11-03T00:00:00Z"),
                **patches,
            ):
                result = db.run_discovery(track_history=True, log_handoff=False)

            history_path = patches["HISTORY_PATH"]
            self.assertTrue(history_path.exists())
            history_entries = yaml.safe_load(history_path.read_text(encoding="utf-8"))
            self.assertEqual(len(history_entries), 1)
            entry = history_entries[0]
            self.assertEqual(entry["blast_radius"]["level"], "system")
            self.assertEqual(result["blast_radius"]["level"], "system")
            self.assertEqual(len(result["insights"]), 3)

    @mock.patch("codexa.cli.discovery_bootstrap.run_discovery")
    def test_cli_text_output(self, mock_run_discovery: mock.MagicMock) -> None:
        mock_run_discovery.return_value = {
            "paths": {"manifest": "analysis/system_manifest.yaml", "change_zones": "analysis/change_zones.md", "intent_map": "analysis/intent_map.md", "metrics": "analysis/metrics.yaml"},
            "blast_radius": {
                "level": "local",
                "changed_zones": ["analysis"],
                "removed_zones": [],
                "notes": ["Artifact digests changed."],
                "recommended_agents": ["discovery_analyzer"],
            },
            "coverage": {"coverage_percent": 80.0},
            "insights": [],
        }

        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            cli.main(["discover", "--output", "text", "--no-history"])

        output = buf.getvalue()
        self.assertIn("Blast radius level: local", output)
        self.assertIn("discovery_analyzer", output)
        self.assertIn("Coverage snapshot: 80.0%", output)
        mock_run_discovery.assert_called_once()
        kwargs = mock_run_discovery.call_args.kwargs
        self.assertEqual(kwargs["project_root"], Path.cwd().resolve())
        self.assertIsNone(kwargs["config_path"])

    @mock.patch("codexa.cli.discovery_bootstrap.run_discovery")
    def test_cli_json_output(self, mock_run_discovery: mock.MagicMock) -> None:
        payload = {
            "paths": {"manifest": "analysis/system_manifest.yaml", "change_zones": "analysis/change_zones.md", "intent_map": "analysis/intent_map.md", "metrics": "analysis/metrics.yaml"},
            "blast_radius": {
                "level": "subsystem",
                "changed_zones": ["analysis", "audit"],
                "removed_zones": ["docs"],
                "notes": [],
                "recommended_agents": ["discovery_analyzer", "requirements_intelligence"],
            },
            "coverage": {"coverage_percent": 70.5},
            "insights": [],
        }

        mock_run_discovery.return_value = payload

        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            cli.main(["discover", "--output", "json", "--no-history"])

        output = buf.getvalue()
        parsed = json.loads(output)
        self.assertEqual(parsed["blast_radius"]["level"], "subsystem")
        self.assertIn("requirements_intelligence", parsed["blast_radius"]["recommended_agents"])
        mock_run_discovery.assert_called_once()
        kwargs = mock_run_discovery.call_args.kwargs
        self.assertEqual(kwargs["project_root"], Path.cwd().resolve())
        self.assertIsNone(kwargs["config_path"])

    @mock.patch("codexa.cli.discovery_bootstrap.run_discovery")
    def test_cli_mode_override_and_flags(self, mock_run_discovery: mock.MagicMock) -> None:
        mock_run_discovery.return_value = {
            "paths": {"manifest": "analysis/system_manifest.yaml", "change_zones": "analysis/change_zones.md", "intent_map": "analysis/intent_map.md", "metrics": "analysis/metrics.yaml"},
            "blast_radius": {"level": "none", "changed_zones": [], "removed_zones": [], "notes": [], "recommended_agents": []},
            "coverage": {"coverage_percent": 75.0},
            "insights": [],
        }

        buf = io.StringIO()
        with mock.patch("sys.stdout", buf):
            cli.main(["discover", "--mode", "quick", "--no-history", "--output", "json"])

        mock_run_discovery.assert_called_once()
        kwargs = mock_run_discovery.call_args.kwargs
        self.assertEqual(kwargs["mode_override"], "quick")
        self.assertFalse(kwargs["track_history"])
        self.assertEqual(kwargs["project_root"], Path.cwd().resolve())


class BlastRadiusPlannerSmokeTest(unittest.TestCase):
    def test_agent_matrix_contains_expected_levels(self) -> None:
        planner = BlastRadiusPlanner()
        self.assertIn("system", planner.AGENT_MATRIX)
        self.assertIn("local", planner.AGENT_MATRIX)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
