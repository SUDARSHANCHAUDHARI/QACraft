import os
import subprocess
import sys
import tempfile
import unittest
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class QACraftInstalledCliTests(unittest.TestCase):
    def run_command(
        self,
        command: list[str],
        *,
        cwd: Path,
        timeout: int = 120,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )

    @staticmethod
    def environment_python(environment: Path) -> Path:
        directory = "Scripts" if os.name == "nt" else "bin"
        executable = "python.exe" if os.name == "nt" else "python"
        return environment / directory / executable

    @staticmethod
    def environment_console(environment: Path) -> Path:
        directory = "Scripts" if os.name == "nt" else "bin"
        executable = "qacraft.exe" if os.name == "nt" else "qacraft"
        return environment / directory / executable

    def test_python_module_entry_point_from_checkout(self):
        result = self.run_command(
            [sys.executable, "-m", "qacraft", "list"],
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("/feature-qa", result.stdout)
        self.assertIn("/release-qa", result.stdout)

    def test_editable_install_exposes_console_and_module_entry_points(self):
        with tempfile.TemporaryDirectory(prefix="qacraft-editable-test-") as parent:
            parent_path = Path(parent)
            environment = parent_path / "venv"
            outside_checkout = parent_path / "outside"
            outside_checkout.mkdir()

            venv.EnvBuilder(with_pip=True).create(environment)
            python = self.environment_python(environment)
            console = self.environment_console(environment)

            install = self.run_command(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--no-deps",
                    "-e",
                    str(ROOT),
                ],
                cwd=outside_checkout,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            self.assertTrue(console.is_file(), console)

            doctor = self.run_command(
                [str(console), "doctor"],
                cwd=outside_checkout,
            )
            self.assertEqual(doctor.returncode, 0, doctor.stderr)
            self.assertIn("QACraft doctor passed.", doctor.stdout)

            evaluation_list = self.run_command(
                [str(python), "-m", "qacraft", "eval-list"],
                cwd=outside_checkout,
            )
            self.assertEqual(evaluation_list.returncode, 0, evaluation_list.stderr)
            self.assertIn("/feature-qa", evaluation_list.stdout)


if __name__ == "__main__":
    unittest.main()
