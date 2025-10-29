import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from pipelines import interaction_stub


class InteractionStubHandlersTest(unittest.TestCase):
    def test_status_requires_no_arguments(self) -> None:
        """TC-FR08-001: `/status` handler validates arguments and payload."""
        response = interaction_stub._handle_status([])
        self.assertEqual(response["command"], "/status")
        with self.assertRaises(ValueError):
            interaction_stub._handle_status(["unexpected"])

    def test_clarify_sets_topic(self) -> None:
        """TC-FR08-001: `/clarify` combines arguments and provides fallback."""
        response = interaction_stub._handle_clarify(["pipeline", "design"])
        self.assertEqual(response["topic"], "pipeline design")
        fallback = interaction_stub._handle_clarify([])
        self.assertEqual(fallback["topic"], "unspecified")

    def test_acknowledge_requires_concern_id(self) -> None:
        """TC-FR08-001: `/ack` enforces concern id requirement."""
        response = interaction_stub._handle_ack(["C-123"])
        self.assertEqual(response["status"], "acknowledged")
        self.assertEqual(response["concern_id"], "C-123")
        with self.assertRaises(ValueError):
            interaction_stub._handle_ack([])

    def test_resolve_accepts_optional_note(self) -> None:
        """TC-FR08-001: `/resolve` supports optional resolution notes."""
        response = interaction_stub._handle_resolve(["C-123", "Fixed", "issue"])
        self.assertEqual(response["status"], "resolved")
        self.assertIn("Fixed issue", response["resolution_note"])
        default = interaction_stub._handle_resolve(["C-123"])
        self.assertEqual(default["resolution_note"], "Resolution recorded.")

    def test_assign_requires_agent_and_concern(self) -> None:
        """TC-FR08-001: `/assign` requires agent and concern arguments."""
        result = interaction_stub._handle_assign(["tester", "C-456"])
        self.assertEqual(result["assigned_to"], "tester")
        self.assertEqual(result["concern_id"], "C-456")
        with self.assertRaises(ValueError):
            interaction_stub._handle_assign(["tester"])

    def test_pause_and_resume_are_argument_free(self) -> None:
        """TC-FR08-001: `/pause` and `/resume` do not accept extraneous arguments."""
        pause = interaction_stub._handle_pause([])
        resume = interaction_stub._handle_resume([])
        self.assertEqual(pause["status"], "paused")
        self.assertEqual(resume["status"], "active")
        with self.assertRaises(ValueError):
            interaction_stub._handle_pause(["now"])

    def test_promote_requires_target_phase(self) -> None:
        """TC-FR08-001: `/promote` requires specifying target phase."""
        response = interaction_stub._handle_promote(["phase2"])
        self.assertEqual(response["target_phase"], "phase2")
        with self.assertRaises(ValueError):
            interaction_stub._handle_promote([])


class InteractionStubCLITest(unittest.TestCase):
    def setUp(self) -> None:
        self.audit_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.audit_dir.cleanup)
        self.original_cwd = Path.cwd()
        # Ensure audit logs write into temp to keep tests isolated.
        self.working = Path(self.audit_dir.name)

    def test_main_unknown_command_returns_error(self) -> None:
        """TC-FR08-001: CLI returns error status for unsupported commands."""
        buffer = io.StringIO()
        with redirect_stderr(buffer):
            code = interaction_stub.main(["stub", "/unknown"])
        self.assertEqual(code, 2)
        self.assertIn("Unknown command", buffer.getvalue())

    def test_main_successful_command_emits_json(self) -> None:
        """TC-FR09-001: CLI emits JSON payload on successful command execution."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = interaction_stub.main(["stub", "/status"])
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["command"], "/status")


if __name__ == "__main__":
    unittest.main()
