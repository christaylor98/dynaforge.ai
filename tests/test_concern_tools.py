import tempfile
import unittest
from pathlib import Path

from pipelines import concern_tools as concern_tools


class ConcernToolsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        self.root = Path(self.tmp_dir.name)
        self.audit_root = self.root / "audit"
        self.project_detail = self.root / "PROJECT_DETAIL.md"
        self._write_placeholder_doc()

    def _write_placeholder_doc(self) -> None:
        text = "\n".join(
            [
                "# Project Detail",
                "",
                "<!-- concerns:start -->",
                "",
                "### Concern Summary",
                "",
                "#### Open Concerns",
                "",
                "- None.",
                "",
                "#### Resolved Concerns",
                "",
                "- None.",
                "",
                "<!-- concerns:end -->",
                "",
            ]
        )
        self.project_detail.write_text(text, encoding="utf-8")

    def test_raise_and_sync_places_concern_in_open_table(self) -> None:
        """TC-FR07-001: Raised concern appears in open Markdown section after sync."""
        entry = concern_tools.raise_concern(
            phase="1",
            raised_by="tester",
            severity="medium",
            message="Sample concern for sync.",
            audit_root=self.audit_root,
        )

        concern_tools.sync_concerns(
            audit_root=self.audit_root,
            project_detail_path=self.project_detail,
        )

        content = self.project_detail.read_text(encoding="utf-8")
        self.assertIn(entry["concern_id"], content)
        self.assertIn("Open Concerns", content)
        self.assertIn("Sample concern for sync.", content)

    def test_resolve_concern_moves_entry_to_resolved_table(self) -> None:
        """TC-FR07-001: Resolved concern moves to resolved section with metadata."""
        entry = concern_tools.raise_concern(
            phase="1",
            raised_by="tester",
            severity="high",
            message="Blocking issue.",
            audit_root=self.audit_root,
        )

        concern_tools.update_concern(
            entry["concern_id"],
            audit_root=self.audit_root,
            note="Investigating root cause.",
        )
        concern_tools.resolve_concern(
            entry["concern_id"],
            resolution="Patched in latest build.",
            audit_root=self.audit_root,
        )

        concern_tools.sync_concerns(
            audit_root=self.audit_root,
            project_detail_path=self.project_detail,
        )

        content = self.project_detail.read_text(encoding="utf-8")
        self.assertIn("Resolved Concerns", content)
        self.assertIn("Patched in latest build.", content)
        open_section = content.split("#### Open Concerns")[1].split("#### Resolved Concerns")[0]
        self.assertNotIn("Blocking issue.", open_section)

        concerns = concern_tools.load_concerns(audit_root=self.audit_root)
        self.assertEqual(len(concerns), 1)
        stored = concerns[0]
        self.assertEqual(stored["resolution"], "Patched in latest build.")
        metadata = stored.get("metadata", {})
        self.assertIn("resolved_timestamp", metadata)
        notes = metadata.get("notes", [])
        self.assertTrue(any(note.get("note") == "Investigating root cause." for note in notes))


if __name__ == "__main__":
    unittest.main()
