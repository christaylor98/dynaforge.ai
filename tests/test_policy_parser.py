import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from pipelines import policy_parser


class TestPolicyParser(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        self.policy_path = Path(self.tmp_dir.name) / "policy.yaml"

    def write_policy(self, data: dict) -> Path:
        self.policy_path.write_text(json.dumps(data), encoding="utf-8")
        return self.policy_path

    def test_validate_policy_success(self) -> None:
        """TC-FR11-001: Policy parser validates well-formed schema."""
        data = {
            "policy": {
                "phase": "0",
                "coverage_threshold": 0.8,
                "reproducibility_threshold": 0.95,
                "gates": [
                    {"id": "coverage", "metric": "coverage", "operator": ">=", "target": 0.8}
                ],
            },
            "notifications": {"on_failure": ["raise_concern"]},
        }
        path = self.write_policy(data)
        loaded = policy_parser.load_policy(path)
        validated = policy_parser.validate_policy(loaded)
        summary = policy_parser.render_summary(validated)

        self.assertIn("Phase: 0", summary)
        self.assertIn("coverage >=", summary)

    def test_missing_policy_section_raises(self) -> None:
        """TC-FR11-001: Policy parser rejects missing policy section."""
        data = {"notifications": {"on_failure": []}}
        path = self.write_policy(data)
        loaded = policy_parser.load_policy(path)
        with self.assertRaises(policy_parser.PolicyValidationError):
            policy_parser.validate_policy(loaded)


if __name__ == "__main__":
    unittest.main()
