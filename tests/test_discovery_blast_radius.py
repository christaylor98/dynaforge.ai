from __future__ import annotations

import unittest

from codexa.discovery import BlastRadiusPlanner, DiscoveryRunRecord


def _sample_metrics(**overrides):
    payload = {
        "metadata": {"generated_at": "2025-11-03T00:00:00Z"},
        "coverage": {"coverage_percent": 75.0},
        "inputs": {"followups_open": []},
        "artifacts": {
            "system_manifest": {"sha256": "aaa"},
            "change_zones": {"sha256": "bbb"},
            "intent_map": {"sha256": "ccc"},
        },
        "zones": [
            {"zone": "analysis", "files": 10, "bytes": 100, "languages": {"python": 10}},
            {"zone": "docs", "files": 5, "bytes": 50, "languages": {"markdown": 5}},
            {"zone": "pipelines", "files": 4, "bytes": 40, "languages": {"python": 4}},
            {"zone": "audit", "files": 3, "bytes": 30, "languages": {"json": 3}},
            {"zone": "tests", "files": 2, "bytes": 20, "languages": {"python": 2}},
        ],
    }
    payload.update(overrides)
    return payload


class BlastRadiusPlannerTest(unittest.TestCase):
    def test_plan_without_previous_defaults_to_system(self) -> None:
        current = DiscoveryRunRecord.from_metrics(_sample_metrics())
        planner = BlastRadiusPlanner()

        result = planner.plan(current, None)

        self.assertEqual(result.level, "system")
        self.assertEqual(result.recommended_agents, BlastRadiusPlanner.AGENT_MATRIX["system"])
        self.assertIn("change_zones", result.changed_artifacts)
        self.assertEqual(result.followups_open, ())

    def test_plan_with_incremental_changes_marks_local(self) -> None:
        previous = DiscoveryRunRecord.from_metrics(
            _sample_metrics(
                artifacts={
                    "system_manifest": {"sha256": "sys-old"},
                    "change_zones": {"sha256": "zones-old"},
                    "intent_map": {"sha256": "intent-same"},
                },
                coverage={"coverage_percent": 75.0},
            )
        )
        current_payload = _sample_metrics(
            artifacts={
                "system_manifest": {"sha256": "sys-new"},
                "change_zones": {"sha256": "zones-new"},
                "intent_map": {"sha256": "intent-same"},
            },
            coverage={"coverage_percent": 75.2},
        )
        # Nudge zone statistics to ensure hash drift.
        current_payload["zones"][0]["files"] = 12
        current = DiscoveryRunRecord.from_metrics(current_payload)

        planner = BlastRadiusPlanner()
        result = planner.plan(current, previous)

        self.assertEqual(result.level, "local")
        self.assertEqual(result.recommended_agents, BlastRadiusPlanner.AGENT_MATRIX["local"])
        self.assertIn("analysis", result.changed_zones)
        self.assertIn("coverage increased", " ".join(result.notes).lower())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
