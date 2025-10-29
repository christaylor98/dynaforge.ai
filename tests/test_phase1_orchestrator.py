import tempfile
import unittest
from pathlib import Path

from pipelines import phase1_orchestrator


class Phase1OrchestratorApprovalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        self.root = Path(self.tmp_dir.name)

    def test_ensure_approval_accepts_document_with_pattern(self) -> None:
        doc = self.root / "approved.md"
        doc.write_text("✅ Approved by Human 2025-10-29\n", encoding="utf-8")
        phase1_orchestrator.ensure_approval(doc, "✅ Approved by Human")
        # No exception means pass.

    def test_ensure_approval_rejects_document_without_pattern(self) -> None:
        doc = self.root / "missing.md"
        doc.write_text("Waiting for approval.\n", encoding="utf-8")
        with self.assertRaises(PermissionError):
            phase1_orchestrator.ensure_approval(doc, "✅ Approved by Human")

    def test_ensure_approval_raises_for_missing_file(self) -> None:
        doc = self.root / "ghost.md"
        with self.assertRaises(FileNotFoundError):
            phase1_orchestrator.ensure_approval(doc, "✅ Approved by Human")


if __name__ == "__main__":
    unittest.main()
