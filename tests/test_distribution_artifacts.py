import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import venv
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WHEEL_REQUIRED = (
    "qacraft/__init__.py",
    "qacraft/__main__.py",
    "qacraft/bundle/.github/workflows/validate.yml",
    "qacraft/bundle/MANIFEST.in",
    "qacraft/bundle/catalog/skills.json",
    "qacraft/bundle/docs/INSTALLATION.md",
    "qacraft/bundle/evaluations/rubrics.json",
    "qacraft/bundle/qacraft/__init__.py",
    "qacraft/bundle/qacraft_build.py",
    "qacraft/bundle/schemas/evaluation-candidate.schema.json",
    "qacraft/bundle/scripts/qacraft.py",
    "qacraft/bundle/scripts/qacraft_installer.py",
    "qacraft/bundle/setup.py",
    "qacraft/bundle/shared/qa-standards.md",
    "qacraft/bundle/skills/feature-qa/SKILL.md",
)

SDIST_REQUIRED_SUFFIXES = (
    "/MANIFEST.in",
    "/catalog/skills.json",
    "/evaluations/rubrics.json",
    "/pyproject.toml",
    "/qacraft/__init__.py",
    "/qacraft_build.py",
    "/schemas/evaluation-candidate.schema.json",
    "/scripts/qacraft.py",
    "/setup.py",
    "/shared/qa-standards.md",
    "/skills/feature-qa/SKILL.md",
    "/tests/test_distribution_artifacts.py",
)


class QACraftDistributionArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="qacraft-artifacts-")
        cls.workspace = Path(cls.temporary.name)
        cls.source = cls.workspace / "source"
        cls.dist = cls.workspace / "dist"
        cls.dist.mkdir()
        shutil.copytree(
            ROOT,
            cls.source,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                ".pytest_cache",
                ".venv",
                "venv",
                "build",
                "dist",
                "*.egg-info",
                "*.pyc",
            ),
        )

        build_environment = cls.workspace / "build-venv"
        venv.EnvBuilder(with_pip=True).create(build_environment)
        build_python = cls.environment_python(build_environment)
        cls.run_command(
            [
                str(build_python),
                "-m",
                "pip",
                "install",
                "build",
                "setuptools>=64",
                "wheel",
            ],
            cwd=cls.workspace,
            timeout=180,
        )
        cls.run_command(
            [
                str(build_python),
                "-m",
                "build",
                "--no-isolation",
                "--sdist",
                "--wheel",
                "--outdir",
                str(cls.dist),
                str(cls.source),
            ],
            cwd=cls.workspace,
            timeout=240,
        )

        wheels = sorted(cls.dist.glob("*.whl"))
        sdists = sorted(cls.dist.glob("*.tar.gz"))
        if len(wheels) != 1 or len(sdists) != 1:
            raise AssertionError(
                f"Expected one wheel and one sdist, found wheels={wheels}, sdists={sdists}"
            )
        cls.wheel = wheels[0]
        cls.sdist = sdists[0]

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    @staticmethod
    def run_command(
        command: list[str],
        *,
        cwd: Path,
        timeout: int = 120,
        expected: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode != expected:
            raise AssertionError(
                f"Command failed ({result.returncode}, expected {expected}): "
                f"{' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

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

    def test_wheel_contains_complete_runtime_bundle(self):
        with zipfile.ZipFile(self.wheel) as archive:
            names = set(archive.namelist())
        for required in WHEEL_REQUIRED:
            with self.subTest(path=required):
                self.assertIn(required, names)
        forbidden = [
            name
            for name in names
            if "__pycache__" in name
            or "/.git/" in name
            or name.endswith((".pyc", ".pyo"))
        ]
        self.assertEqual(forbidden, [])

    def test_source_distribution_contains_build_inputs_and_canonical_sources(self):
        with tarfile.open(self.sdist, "r:gz") as archive:
            names = set(archive.getnames())
        for suffix in SDIST_REQUIRED_SUFFIXES:
            with self.subTest(path=suffix):
                self.assertTrue(any(name.endswith(suffix) for name in names), suffix)
        forbidden = [
            name
            for name in names
            if "__pycache__" in name
            or "/.git/" in name
            or name.endswith((".pyc", ".pyo"))
        ]
        self.assertEqual(forbidden, [])

    def test_built_artifacts_install_and_run_complete_lifecycle(self):
        for label, artifact in (("wheel", self.wheel), ("sdist", self.sdist)):
            with self.subTest(artifact=label):
                self.assert_artifact_lifecycle(label, artifact)

    def assert_artifact_lifecycle(self, label: str, artifact: Path) -> None:
        environment = self.workspace / f"venv-{label}"
        outside = self.workspace / f"outside-{label}"
        project = self.workspace / f"project-{label}"
        outside.mkdir()
        project.mkdir()
        unrelated = project / "keep-me.txt"
        unrelated.write_text("unrelated\n", encoding="utf-8")

        venv.EnvBuilder(with_pip=True).create(environment)
        python = self.environment_python(environment)
        console = self.environment_console(environment)
        self.run_command(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-deps",
                str(artifact),
            ],
            cwd=outside,
            timeout=180,
        )

        doctor = self.run_command([str(console), "doctor"], cwd=outside)
        self.assertIn("QACraft doctor passed.", doctor.stdout)

        evaluation_list = self.run_command(
            [str(python), "-m", "qacraft", "eval-list"], cwd=outside
        )
        self.assertIn("/feature-qa", evaluation_list.stdout)

        runtime = Path(
            self.run_command(
                [
                    str(python),
                    "-c",
                    "import qacraft; print(qacraft.runtime_root())",
                ],
                cwd=outside,
            ).stdout.strip()
        )
        self.assertTrue((runtime / "scripts" / "qacraft.py").is_file())
        self.assertEqual(runtime.name, "bundle")

        release = self.run_command(
            [str(console), "release-check", "--json"], cwd=outside
        )
        self.assertTrue(json.loads(release.stdout)["passed"])

        candidate = runtime / "evaluations" / "examples" / "feature-qa-pass.json"
        evaluation = self.run_command(
            [str(console), "evaluate", "--input", str(candidate)], cwd=outside
        )
        self.assertTrue(json.loads(evaluation.stdout)["passed"])

        self.run_command(
            [
                str(console),
                "install",
                "feature-qa",
                "--agent",
                "codex",
                "--destination",
                str(project),
                "--apply",
            ],
            cwd=outside,
        )
        self.run_command(
            [
                str(console),
                "verify-install",
                "--agent",
                "codex",
                "--destination",
                str(project),
            ],
            cwd=outside,
        )
        self.run_command(
            [
                str(console),
                "uninstall",
                "--agent",
                "codex",
                "--destination",
                str(project),
                "--apply",
            ],
            cwd=outside,
        )
        self.assertTrue(unrelated.is_file())
        self.assertFalse((project / ".agents" / "qacraft" / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
