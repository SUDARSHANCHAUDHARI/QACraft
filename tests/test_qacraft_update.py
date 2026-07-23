import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "qacraft.py"
sys.path.insert(0, str(ROOT / "scripts"))

from qacraft_installer import InstallError  # noqa: E402
from qacraft_updater import apply_update_plan, build_update_plan  # noqa: E402


class QACraftUpdateTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def install_feature_qa(self, destination: Path) -> None:
        destination.mkdir()
        result = self.run_cli(
            "install",
            "feature-qa",
            "--destination",
            str(destination),
            "--apply",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_update_preview_performs_no_writes(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_feature_qa(destination)
            before = (destination / ".qacraft-manifest.json").read_bytes()

            result = self.run_cli(
                "update",
                "feature-qa",
                "bug-report",
                "--destination",
                str(destination),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["mode"], "preview-only")
            self.assertFalse(plan["writes_performed"])
            self.assertFalse((destination / "skills/bug-report/SKILL.md").exists())
            self.assertEqual((destination / ".qacraft-manifest.json").read_bytes(), before)

    def test_update_apply_adds_and_removes_manifest_owned_files(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_feature_qa(destination)
            unrelated = destination / "keep-me.txt"
            unrelated.write_text("user file", encoding="utf-8")

            add_result = self.run_cli(
                "update",
                "feature-qa",
                "bug-report",
                "--destination",
                str(destination),
                "--apply",
            )
            self.assertEqual(add_result.returncode, 0, add_result.stderr)
            self.assertTrue((destination / "skills/bug-report/SKILL.md").is_file())

            remove_result = self.run_cli(
                "update",
                "bug-report",
                "--destination",
                str(destination),
                "--apply",
            )
            self.assertEqual(remove_result.returncode, 0, remove_result.stderr)
            self.assertFalse((destination / "skills/feature-qa/SKILL.md").exists())
            self.assertTrue((destination / "skills/bug-report/SKILL.md").is_file())
            self.assertTrue(unrelated.is_file())

            manifest = json.loads((destination / ".qacraft-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["skills"], ["bug-report"])

    def test_update_refuses_modified_installation(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_feature_qa(destination)
            changed = destination / "skills/feature-qa/SKILL.md"
            changed.write_text("user modification", encoding="utf-8")

            result = self.run_cli(
                "update",
                "feature-qa",
                "bug-report",
                "--destination",
                str(destination),
                "--apply",
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("missing or modified", result.stderr)
            self.assertEqual(changed.read_text(encoding="utf-8"), "user modification")
            self.assertFalse((destination / "skills/bug-report/SKILL.md").exists())

    def test_apply_refuses_destination_change_after_preview(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_feature_qa(destination)
            sources = [
                "skills/feature-qa/SKILL.md",
                "skills/feature-qa/templates/report.yaml",
                "skills/feature-qa/examples/request.md",
                "skills/feature-qa/examples/expected-output.md",
                "skills/bug-report/SKILL.md",
                "skills/bug-report/templates/report.yaml",
                "skills/bug-report/examples/request.md",
                "skills/bug-report/examples/expected-output.md",
                "shared/qa-standards.md",
                "shared/security-boundaries.md",
                "shared/approval-policy.md",
                "shared/evidence-policy.md",
                "shared/data-safety.md",
                "shared/result-model.md",
                "shared/publication-policy.md",
                "shared/release-policy.md",
            ]
            plan = build_update_plan(
                ROOT,
                destination,
                sources,
                qacraft_version="1.0.0",
                agent="generic",
                skills=["feature-qa", "bug-report"],
            )
            raced = destination / "skills/bug-report/SKILL.md"
            raced.parent.mkdir(parents=True, exist_ok=True)
            raced.write_text("unowned file", encoding="utf-8")

            with self.assertRaisesRegex(InstallError, "Destination changed"):
                apply_update_plan(plan)
            self.assertEqual(raced.read_text(encoding="utf-8"), "unowned file")


if __name__ == "__main__":
    unittest.main()
