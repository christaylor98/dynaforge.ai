import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import audit.logger as audit_logger
import agents.designer as designer_module
import agents.implementer as implementer_module
import agents.project_manager as pm_module
import agents.tester as tester_module
import pipelines.phase1_orchestrator as orchestrator_module


class _BaseAgentTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.root = Path(self._tmpdir.name)
        self.audit_root = self.root / "audit"

        # Swap the default audit logger so handoff events stay within the temp directory.
        self._original_logger = audit_logger._DEFAULT_LOGGER
        audit_logger._DEFAULT_LOGGER = audit_logger.AuditLogger(root=self.audit_root)
        self.addCleanup(self._restore_logger)

    def _restore_logger(self) -> None:
        audit_logger._DEFAULT_LOGGER = self._original_logger

    def _load_handoff_entries(self) -> list[dict]:
        handoff_path = self.audit_root / "handoff.jsonl"
        if not handoff_path.exists():
            return []
        entries: list[dict] = []
        for line in handoff_path.read_text(encoding="utf-8").splitlines():
            entries.append(json.loads(line))
        return entries

    def patch_module_attrs(self, module: object, **updates: object) -> None:
        originals = {name: getattr(module, name) for name in updates}

        def _restore() -> None:
            for name, value in originals.items():
                setattr(module, name, value)

        for name, value in updates.items():
            setattr(module, name, value)
        self.addCleanup(_restore)


class ProjectManagerIntegrationTest(_BaseAgentTest):
    def setUp(self) -> None:
        super().setUp()
        self.docs_dir = self.root / "docs"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        # Seed a minimal requirements table so the project manager can summarize it.
        requirements_path = self.docs_dir / "REQUIREMENTS.md"
        requirements_path.write_text(
            "\n".join(
                [
                    "| ID | Requirement | Notes / Rationale |",
                    "| -- | ----------- | ----------------- |",
                    "| FR-01 | Project Manager agent | Coordinates documentation |",
                    "| FR-02 | Status docs | Keep overview current |",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        self.patch_module_attrs(
            pm_module,
            PROJECT_ROOT=self.root,
            DOCS_DIR=self.docs_dir,
            REQUIREMENTS_PATH=requirements_path,
            OVERVIEW_PATH=self.docs_dir / "PROJECT_OVERVIEW.md",
            DETAIL_PATH=self.docs_dir / "PROJECT_DETAIL.md",
        )

    def test_run_writes_documents_and_audit_handoff(self) -> None:
        """TC-FR01-001: Project Manager refreshes docs and logs handoff."""
        manager = pm_module.ProjectManager(phase="1")
        manager.run()

        overview_content = pm_module.OVERVIEW_PATH.read_text(encoding="utf-8")
        detail_content = pm_module.DETAIL_PATH.read_text(encoding="utf-8")
        self.assertIn("# Project Overview", overview_content)
        self.assertIn("Phase:", overview_content)
        self.assertIn("FR-01", detail_content)

        entries = self._load_handoff_entries()
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["record_type"], "handoff")
        self.assertEqual(entry["from_agent"], "project_manager")
        self.assertIn("docs/PROJECT_OVERVIEW.md", entry["artifacts"])
        self.assertIn("docs/PROJECT_DETAIL.md", entry["artifacts"])


class DesignerIntegrationTest(_BaseAgentTest):
    def setUp(self) -> None:
        super().setUp()
        self.design_dir = self.root / "design"
        self.design_dir.mkdir(parents=True, exist_ok=True)
        self.brief_path = self.root / "brief.md"
        self.brief_path.write_text("# Brief\n", encoding="utf-8")

        self.patch_module_attrs(
            designer_module,
            PROJECT_ROOT=self.root,
            DESIGN_DIR=self.design_dir,
            DESIGN_SPEC_PATH=self.design_dir / "DESIGN_SPEC.md",
        )

    def test_create_design_spec_populates_sections_and_logs_handoff(self) -> None:
        """TC-FR03-001: Designer emits design spec referenced in trace matrix."""
        scenario = {"title": "Concern Lifecycle", "objective": "Harden concern tracking."}
        designer = designer_module.Designer(phase="1")
        output = designer.create_design_spec(scenario, brief_path=self.brief_path)

        content = output.read_text(encoding="utf-8")
        self.assertIn("# Design Spec — Concern Lifecycle", content)
        self.assertIn("Source brief", content)
        self.assertIn("Concern ingestion service", content)

        entries = self._load_handoff_entries()
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["from_agent"], "designer")
        self.assertIn("design/DESIGN_SPEC.md", entry["artifacts"][0])


class ImplementerIntegrationTest(_BaseAgentTest):
    def setUp(self) -> None:
        super().setUp()
        self.docs_dir = self.root / "docs"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.design_path = self.docs_dir / "DESIGN_SPEC.md"
        self.design_path.write_text("# Design Spec", encoding="utf-8")

        self.patch_module_attrs(
            implementer_module,
            PROJECT_ROOT=self.root,
            DOCS_DIR=self.docs_dir,
            IMPLEMENTATION_PLAN_PATH=self.docs_dir / "IMPLEMENTATION_PLAN.md",
        )

    def test_create_execution_plan_lists_tasks_and_logs_handoff(self) -> None:
        """TC-FR04-001: Implementer produces execution plan tied to design reference."""
        scenario = {"title": "Concern Lifecycle", "focus_areas": ["Lifecycle automation"]}
        implementer = implementer_module.Implementer(phase="1")
        output = implementer.create_execution_plan(scenario, design_path=self.design_path)

        content = output.read_text(encoding="utf-8")
        self.assertIn("# Implementation Plan — Concern Lifecycle", content)
        self.assertIn("- [ ] Extend audit logger utilities", content)
        self.assertIn("Design reference", content)

        entries = self._load_handoff_entries()
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["from_agent"], "implementer")
        self.assertIn("docs/IMPLEMENTATION_PLAN.md", entry["artifacts"][0])


class TesterIntegrationTest(_BaseAgentTest):
    def setUp(self) -> None:
        super().setUp()

        tests_dir = self.root / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        self.patch_module_attrs(
            tester_module,
            PROJECT_ROOT=self.root,
            TESTS_DIR=tests_dir,
            TEST_PLAN_PATH=tests_dir / "TEST_PLAN.md",
            TEST_RESULTS_PATH=tests_dir / "TEST_RESULTS.md",
        )

    def test_prepare_phase_test_assets_generates_plan_and_results(self) -> None:
        """TC-FR05-001: Tester prepares phase test assets and logs handoff."""
        scenario = {"title": "Concern Lifecycle", "objective": "Verify QA posture."}
        tester = tester_module.Tester(phase="1")
        plan_path, results_path = tester.prepare_phase_test_assets(scenario)

        plan_content = plan_path.read_text(encoding="utf-8")
        results_content = results_path.read_text(encoding="utf-8")
        self.assertIn("# Test Plan — Phase 1", plan_content)
        self.assertIn("Validate concern logging mirrors into Markdown summaries.", plan_content)
        self.assertIn("Test Results — Phase 1", results_content)

        entries = self._load_handoff_entries()
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["from_agent"], "tester")
        self.assertIn("tests/TEST_PLAN.md", entry["artifacts"])
        self.assertIn("tests/TEST_RESULTS.md", entry["artifacts"])


class Phase1OrchestratorIntegrationTest(_BaseAgentTest):
    def setUp(self) -> None:
        super().setUp()
        self.docs_dir = self.root / "docs"
        self.design_dir = self.root / "design"
        self.tests_dir = self.root / "tests"
        for path in (self.docs_dir, self.design_dir, self.tests_dir):
            path.mkdir(parents=True, exist_ok=True)

        requirements_path = self.docs_dir / "REQUIREMENTS.md"
        requirements_path.write_text(
            "\n".join(
                [
                    "| ID | Requirement | Notes / Rationale |",
                    "| -- | ----------- | ----------------- |",
                    "| FR-01 | Project Manager agent | Coordinates documentation |",
                    "| FR-02 | Status docs | Keep overview current |",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        self.patch_module_attrs(
            pm_module,
            PROJECT_ROOT=self.root,
            DOCS_DIR=self.docs_dir,
            REQUIREMENTS_PATH=requirements_path,
            OVERVIEW_PATH=self.docs_dir / "PROJECT_OVERVIEW.md",
            DETAIL_PATH=self.docs_dir / "PROJECT_DETAIL.md",
        )

        self.patch_module_attrs(
            designer_module,
            PROJECT_ROOT=self.root,
            DESIGN_DIR=self.design_dir,
            DESIGN_SPEC_PATH=self.design_dir / "DESIGN_SPEC.md",
        )

        self.patch_module_attrs(
            implementer_module,
            PROJECT_ROOT=self.root,
            DOCS_DIR=self.docs_dir,
            IMPLEMENTATION_PLAN_PATH=self.docs_dir / "IMPLEMENTATION_PLAN.md",
        )

        self.patch_module_attrs(
            tester_module,
            PROJECT_ROOT=self.root,
            TESTS_DIR=self.tests_dir,
            TEST_PLAN_PATH=self.tests_dir / "TEST_PLAN.md",
            TEST_RESULTS_PATH=self.tests_dir / "TEST_RESULTS.md",
        )

        artifacts_root = self.root / "artifacts" / "phase1" / "orchestration"
        self.patch_module_attrs(
            orchestrator_module,
            PROJECT_ROOT=self.root,
            ARTIFACT_ROOT=artifacts_root,
            SUMMARY_PATH=artifacts_root / "summary.json",
        )

    def test_orchestrate_writes_summary_and_expected_artifacts(self) -> None:
        """TC-FR01-002: Phase 1 orchestrator executes end-to-end loop."""
        summary = orchestrator_module.orchestrate()
        summary_path = orchestrator_module.SUMMARY_PATH
        self.assertTrue(summary_path.exists())

        saved_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(saved_summary["scenario"]["phase"], "1")

        entries = self._load_handoff_entries()
        # Expect handoffs from project manager (brief), designer, implementer, tester.
        self.assertGreaterEqual(len(entries), 4)
        phases = {entry["from_agent"] for entry in entries}
        self.assertIn("project_manager", phases)
        self.assertIn("designer", phases)
        self.assertIn("implementer", phases)
        self.assertIn("tester", phases)

        for artifact in summary["artifacts"].values():
            artifact_path = self.root / artifact
            self.assertTrue(artifact_path.exists(), f"Missing artifact {artifact_path}")


if __name__ == "__main__":
    unittest.main()
