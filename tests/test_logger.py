import json
import tempfile
import unittest
from pathlib import Path

from audit import AuditLogger


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class TestAuditLogger(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        self.root = Path(self.tmp_dir.name)

    def test_log_handoff_writes_schema_compliant_entry(self) -> None:
        """TC-FR06-001: Handoff entries persist with schema-compliant structure."""
        logger = AuditLogger(root=self.root, schema_version="0.1.0-test")
        entry = logger.log_handoff(
            phase="0",
            from_agent="implementer",
            to_agent="tester",
            summary="Skeleton ready.",
            artifacts=["docs/PROJECT_OVERVIEW.md"],
            concerns=[],
            metadata={"notes": "unit-test"},
        )

        handoff_file = self.root / "handoff.jsonl"
        contents = read_jsonl(handoff_file)

        self.assertEqual(entry["record_type"], "handoff")
        self.assertEqual(entry["schema_version"], "0.1.0-test")
        self.assertEqual(entry["summary"], "Skeleton ready.")
        self.assertEqual(contents, [entry])

    def test_log_concern_rejects_unknown_severity(self) -> None:
        """TC-FR06-001: Concern logger rejects unsupported severity values."""
        logger = AuditLogger(root=self.root)

        with self.assertRaisesRegex(ValueError, "Unsupported severity"):
            logger.log_concern(
                phase="0",
                raised_by="tester",
                severity="invalid",
                message="Bad severity",
            )

    def test_log_command_persists_arguments(self) -> None:
        """TC-FR06-001: Command entries capture arguments and metadata."""
        logger = AuditLogger(root=self.root)
        entry = logger.log_command(
            phase="0",
            issued_by="interaction_stub",
            command="/clarify",
            arguments=["scope"],
            metadata={"response_id": "abc"},
        )

        command_file = self.root / "commands.jsonl"
        contents = read_jsonl(command_file)

        self.assertEqual(entry["command"], "/clarify")
        self.assertEqual(entry["arguments"], ["scope"])
        self.assertEqual(contents, [entry])


if __name__ == "__main__":
    unittest.main()
