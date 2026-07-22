import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "qacraft.py"


class QACraftCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def test_list_includes_core_skills(self):
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("/feature-qa", result.stdout)
        self.assertIn("/bug-report", result.stdout)
        self.assertIn("/release-qa", result.stdout)

    def test_doctor_passes_for_repository(self):
        result = self.run_cli("doctor")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("QACraft doctor passed.", result.stdout)
        self.assertIn(
            "Generic install, update, verification, and uninstall: available",
            result.stdout,
        )
        self.assertIn(
            "Verified Codex and Claude Code adapters: available",
            result.stdout,
        )

    def test_plan_install_is_preview_only_and_complete(self):
        with tempfile.TemporaryDirectory() as destination:
            result = self.run_cli(
                "plan-install",
                "feature-qa",
                "bug-report",
                "--agent",
                "generic",
                "--destination",
                destination,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["mode"], "preview-only")
            self.assertFalse(plan["writes_performed"])
            self.assertEqual(plan["agent"], "generic")
            self.assertEqual(plan["skills"], ["bug-report", "feature-qa"])
            self.assertIn("release-policy.md", plan["shared_policies"])
            self.assertIn("shared/release-policy.md", plan["source_files"])
            self.assertIn("skills/feature-qa/SKILL.md", plan["source_files"])
            self.assertIn(
                "skills/bug-report/templates/report.yaml",
                plan["source_files"],
            )
            self.assertEqual(list(Path(destination).iterdir()), [])

    def test_generic_install_without_apply_is_preview_only(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "skills"
            result = self.run_cli(
                "install",
                "feature-qa",
                "--destination",
                str(destination),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["mode"], "preview-only")
            self.assertFalse(plan["writes_performed"])
            self.assertFalse(destination.exists())

    def test_generic_install_apply_creates_files_and_manifest(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "skills"
            result = self.run_cli(
                "install",
                "feature-qa",
                "--destination",
                str(destination),
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["mode"], "applied")
            self.assertTrue(output["writes_performed"])

            installed = destination / "skills" / "feature-qa" / "SKILL.md"
            manifest_path = destination / ".qacraft-manifest.json"
            self.assertTrue(installed.is_file())
            self.assertTrue(manifest_path.is_file())

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["agent"], "generic")
            self.assertEqual(manifest["skills"], ["feature-qa"])
            record = next(
                item
                for item in manifest["files"]
                if item["path"] == "skills/feature-qa/SKILL.md"
            )
            actual_hash = hashlib.sha256(installed.read_bytes()).hexdigest()
            self.assertEqual(record["sha256"], actual_hash)

    def test_generic_install_refuses_existing_destination_file(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "skills"
            conflict = destination / "skills" / "feature-qa" / "SKILL.md"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("keep me", encoding="utf-8")

            result = self.run_cli(
                "install",
                "feature-qa",
                "--destination",
                str(destination),
                "--apply",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("already exist", result.stderr)
            self.assertEqual(conflict.read_text(encoding="utf-8"), "keep me")
            self.assertFalse((destination / ".qacraft-manifest.json").exists())

    def test_codex_install_preview_uses_verified_layout(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "project"
            destination.mkdir()
            result = self.run_cli(
                "install",
                "feature-qa",
                "--agent",
                "codex",
                "--destination",
                str(destination),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["agent"], "codex")
            self.assertIn(
                ".agents/skills/feature-qa/SKILL.md",
                plan["target_files"],
            )
            self.assertEqual(
                plan["manifest_relative"],
                ".agents/qacraft/manifest.json",
            )
            self.assertFalse((destination / ".agents").exists())

    def test_plan_install_rejects_unknown_skill(self):
        result = self.run_cli(
            "plan-install",
            "does-not-exist",
            "--destination",
            "/tmp/qacraft-preview",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown skill", result.stderr)

    def test_plan_install_rejects_all_with_explicit_skills(self):
        result = self.run_cli(
            "plan-install",
            "feature-qa",
            "--all",
            "--destination",
            "/tmp/qacraft-preview",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("either explicit skills or --all", result.stderr)


if __name__ == "__main__":
    unittest.main()
