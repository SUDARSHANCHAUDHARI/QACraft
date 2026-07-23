import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "qacraft.py"


class QACraftUninstallTests(unittest.TestCase):
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
            "--agent",
            "generic",
            "--destination",
            str(destination),
            "--apply",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_verify_install_reports_healthy_installation(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_feature_qa(destination)
            result = self.run_cli("verify-install", "--destination", str(destination))
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["healthy"])
            self.assertTrue(all(item["status"] == "ok" for item in report["files"]))

    def test_verify_install_detects_modified_file(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_feature_qa(destination)
            changed = destination / "skills" / "feature-qa" / "SKILL.md"
            changed.write_text(changed.read_text(encoding="utf-8") + "\nmodified\n", encoding="utf-8")
            result = self.run_cli("verify-install", "--destination", str(destination))
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertFalse(report["healthy"])
            self.assertIn("modified", {item["status"] for item in report["files"]})

    def test_uninstall_preview_performs_no_writes(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_feature_qa(destination)
            before = sorted(path.relative_to(destination).as_posix() for path in destination.rglob("*") if path.is_file())
            result = self.run_cli("uninstall", "--destination", str(destination))
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            self.assertFalse(plan["writes_performed"])
            after = sorted(path.relative_to(destination).as_posix() for path in destination.rglob("*") if path.is_file())
            self.assertEqual(before, after)

    def test_uninstall_apply_removes_only_manifest_owned_files(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_feature_qa(destination)
            unrelated = destination / "keep-me.txt"
            unrelated.write_text("user file", encoding="utf-8")
            result = self.run_cli("uninstall", "--destination", str(destination), "--apply")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(unrelated.exists())
            self.assertFalse((destination / ".qacraft-manifest.json").exists())
            self.assertFalse((destination / "skills" / "feature-qa" / "SKILL.md").exists())

    def test_uninstall_refuses_modified_files(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_feature_qa(destination)
            changed = destination / "skills" / "feature-qa" / "SKILL.md"
            changed.write_text("user changed this file", encoding="utf-8")
            result = self.run_cli("uninstall", "--destination", str(destination), "--apply")
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing or modified", result.stderr)
            self.assertTrue(changed.exists())
            self.assertTrue((destination / ".qacraft-manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
