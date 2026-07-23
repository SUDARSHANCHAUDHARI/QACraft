import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "qacraft.py"
sys.path.insert(0, str(ROOT / "scripts"))

from release_check import run_release_checks  # noqa: E402


class QACraftReleaseCheckTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def copy_repository(self, parent: str) -> Path:
        destination = Path(parent) / "repo"
        shutil.copytree(
            ROOT,
            destination,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                ".pytest_cache",
                ".venv",
                "venv",
                "dist",
                "build",
            ),
        )
        return destination

    def test_release_check_passes_for_repository(self):
        report = run_release_checks(ROOT)
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["version"], "1.4.1")
        self.assertEqual(report["summary"]["failed_checks"], [])

    def test_release_check_cli_emits_json(self):
        result = self.run_cli("release-check", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["passed"])
        self.assertEqual(report["version"], "1.4.1")

    def test_release_check_detects_missing_release_file(self):
        with tempfile.TemporaryDirectory() as parent:
            repository = self.copy_repository(parent)
            (repository / "docs" / "INSTALLATION.md").unlink()
            report = run_release_checks(repository)
            self.assertFalse(report["passed"])
            self.assertIn("release_files", report["summary"]["failed_checks"])

    def test_release_check_detects_rubric_drift(self):
        with tempfile.TemporaryDirectory() as parent:
            repository = self.copy_repository(parent)
            rubric_path = repository / "evaluations" / "rubrics.json"
            rubrics = json.loads(rubric_path.read_text(encoding="utf-8"))
            rubrics["skills"]["test-plan"]["required_outputs"].pop()
            rubric_path.write_text(json.dumps(rubrics, indent=2) + "\n", encoding="utf-8")
            report = run_release_checks(repository)
            self.assertFalse(report["passed"])
            self.assertIn("rubric_skill_binding", report["summary"]["failed_checks"])

    def test_release_check_detects_fixture_expectation_drift(self):
        with tempfile.TemporaryDirectory() as parent:
            repository = self.copy_repository(parent)
            fixture_path = repository / "evaluations" / "fixtures.json"
            fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))
            target = next(
                item
                for item in fixtures["fixtures"]
                if item["path"] == "fixtures/api-qa-secret-output.json"
            )
            target["expected_pass"] = True
            target.pop("expected_failed_checks")
            fixture_path.write_text(
                json.dumps(fixtures, indent=2) + "\n",
                encoding="utf-8",
            )
            report = run_release_checks(repository)
            self.assertFalse(report["passed"])
            self.assertIn("published_fixtures", report["summary"]["failed_checks"])

    def test_release_check_detects_missing_fixture_file(self):
        with tempfile.TemporaryDirectory() as parent:
            repository = self.copy_repository(parent)
            (
                repository
                / "evaluations"
                / "examples"
                / "staged-rollout-check-pass.json"
            ).unlink()
            report = run_release_checks(repository)
            self.assertFalse(report["passed"])
            self.assertIn("published_fixtures", report["summary"]["failed_checks"])

    def test_release_check_detects_expanded_ci_matrix(self):
        with tempfile.TemporaryDirectory() as parent:
            repository = self.copy_repository(parent)
            workflow_path = repository / ".github" / "workflows" / "validate.yml"
            workflow = workflow_path.read_text(encoding="utf-8")
            workflow = workflow.replace(
                'python-version: "3.12"',
                'python-version: "3.12"\n\n  second-job:\n    runs-on: ubuntu-latest',
            )
            workflow_path.write_text(workflow, encoding="utf-8")
            report = run_release_checks(repository)
            self.assertFalse(report["passed"])
            self.assertIn("lean_ci", report["summary"]["failed_checks"])

    def test_release_check_detects_missing_editable_entry_point(self):
        with tempfile.TemporaryDirectory() as parent:
            repository = self.copy_repository(parent)
            (repository / "qacraft" / "__main__.py").unlink()
            report = run_release_checks(repository)
            self.assertFalse(report["passed"])
            self.assertIn("editable_cli", report["summary"]["failed_checks"])

    def test_release_check_detects_incomplete_distribution_recipe(self):
        with tempfile.TemporaryDirectory() as parent:
            repository = self.copy_repository(parent)
            pyproject = repository / "pyproject.toml"
            content = pyproject.read_text(encoding="utf-8").replace(
                'distribution_mode = "bundled-artifacts"',
                'distribution_mode = "editable-source"',
            )
            pyproject.write_text(content, encoding="utf-8")
            report = run_release_checks(repository)
            self.assertFalse(report["passed"])
            self.assertIn("distribution_bundle", report["summary"]["failed_checks"])


if __name__ == "__main__":
    unittest.main()
