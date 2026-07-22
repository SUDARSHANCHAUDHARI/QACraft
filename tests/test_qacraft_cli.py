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
        self.assertIn("Write operations: disabled", result.stdout)

    def test_plan_install_is_preview_only(self):
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
            self.assertEqual(list(Path(destination).iterdir()), [])

    def test_plan_install_rejects_unknown_skill(self):
        result = self.run_cli(
            "plan-install",
            "does-not-exist",
            "--destination",
            "/tmp/qacraft-preview",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown skill", result.stderr)


if __name__ == "__main__":
    unittest.main()
