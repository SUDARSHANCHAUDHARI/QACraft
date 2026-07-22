import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "qacraft.py"
sys.path.insert(0, str(ROOT / "scripts"))

from qacraft_adapters import (  # noqa: E402
    ADAPTERS,
    AGENT_SKILL_TRANSFORM,
    build_file_specs,
    layout_for,
)


EXPECTED_ADAPTERS = {
    "generic": ("skills", ".qacraft-manifest.json"),
    "codex": (".agents/skills", ".agents/qacraft/manifest.json"),
    "claude-code": (".claude/skills", ".claude/qacraft/manifest.json"),
    "github-copilot": (".github/skills", ".github/qacraft/manifest.json"),
    "gemini-cli": (".gemini/skills", ".gemini/qacraft/manifest.json"),
    "opencode": (".opencode/skills", ".opencode/qacraft/manifest.json"),
}


class QACraftAdapterTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def install(
        self,
        destination: Path,
        agent: str,
        *skills: str,
    ) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "install",
            *skills,
            "--agent",
            agent,
            "--destination",
            str(destination),
            "--apply",
        )

    def verify(self, destination: Path, agent: str) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "verify-install",
            "--agent",
            agent,
            "--destination",
            str(destination),
        )

    def uninstall(self, destination: Path, agent: str) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "uninstall",
            "--agent",
            agent,
            "--destination",
            str(destination),
            "--apply",
        )

    def test_verified_adapter_layouts(self):
        self.assertEqual(set(ADAPTERS), set(EXPECTED_ADAPTERS))
        for agent, (skills_root, manifest_path) in EXPECTED_ADAPTERS.items():
            with self.subTest(agent=agent):
                layout = layout_for(agent)
                self.assertEqual(layout.agent, agent)
                self.assertEqual(layout.skills_root.as_posix(), skills_root)
                self.assertEqual(layout.manifest_path.as_posix(), manifest_path)

        expected_docs = {
            "github-copilot": "https://docs.github.com/en/copilot/",
            "gemini-cli": "https://geminicli.com/docs/cli/skills/",
            "opencode": "https://opencode.ai/docs/skills",
        }
        for agent, prefix in expected_docs.items():
            with self.subTest(documentation=agent):
                self.assertTrue(layout_for(agent).documentation.startswith(prefix))

        copilot_specs = build_file_specs(
            "github-copilot",
            ["feature-qa"],
            ["qa-standards.md"],
        )
        self.assertIn(
            {
                "source": "skills/feature-qa/SKILL.md",
                "target": ".github/skills/feature-qa/SKILL.md",
                "transform": AGENT_SKILL_TRANSFORM,
            },
            copilot_specs,
        )
        self.assertIn(
            {
                "source": "shared/qa-standards.md",
                "target": ".github/qacraft/shared/qa-standards.md",
            },
            copilot_specs,
        )

    def test_installed_agent_skills_use_standard_frontmatter(self):
        native_roots = {
            "github-copilot": ".github/skills",
            "gemini-cli": ".gemini/skills",
            "opencode": ".opencode/skills",
        }
        source = (ROOT / "skills/feature-qa/SKILL.md").read_text(encoding="utf-8")
        source_body = source.split("\n---\n", 1)[1]

        for agent, root in native_roots.items():
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as parent:
                project = Path(parent) / "project"
                project.mkdir()
                result = self.install(project, agent, "feature-qa")
                self.assertEqual(result.returncode, 0, result.stderr)

                installed_path = project / root / "feature-qa/SKILL.md"
                installed = installed_path.read_text(encoding="utf-8")
                frontmatter = installed.split("---", 2)[1]
                installed_body = installed.split("\n---\n", 1)[1]

                self.assertIn('name: "feature-qa"', frontmatter)
                self.assertIn('description: "Turns a ticket', frontmatter)
                self.assertIn("metadata:", frontmatter)
                self.assertIn('qacraft-command: "/feature-qa"', frontmatter)
                self.assertNotIn("\ncommand:", frontmatter)
                self.assertEqual(installed_body, source_body)

                manifest = json.loads(
                    (project / layout_for(agent).manifest_path).read_text(encoding="utf-8")
                )
                record = next(
                    item
                    for item in manifest["files"]
                    if item["path"] == f"{root}/feature-qa/SKILL.md"
                )
                self.assertEqual(record["transform"], AGENT_SKILL_TRANSFORM)
                self.assertNotEqual(record["source_sha256"], record["sha256"])

    def test_all_verified_agent_installations_can_coexist(self):
        installed_skills = {
            "codex": "feature-qa",
            "claude-code": "bug-report",
            "github-copilot": "ticket-review",
            "gemini-cli": "verify-fix",
            "opencode": "release-qa",
        }
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "project"
            project.mkdir()

            for agent, skill in installed_skills.items():
                result = self.install(project, agent, skill)
                self.assertEqual(result.returncode, 0, result.stderr)

            for agent, skill in installed_skills.items():
                with self.subTest(agent=agent):
                    layout = layout_for(agent)
                    self.assertTrue((project / layout.skills_root / skill / "SKILL.md").is_file())
                    self.assertTrue((project / layout.manifest_path).is_file())
                    verified = self.verify(project, agent)
                    self.assertEqual(verified.returncode, 0, verified.stderr)
                    self.assertEqual(json.loads(verified.stdout)["agent"], agent)

            self.assertFalse((project / ".qacraft-manifest.json").exists())

    def test_new_adapter_update_uses_independent_manifest(self):
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "project"
            project.mkdir()
            installed = self.install(project, "gemini-cli", "feature-qa")
            self.assertEqual(installed.returncode, 0, installed.stderr)

            updated = self.run_cli(
                "update",
                "feature-qa",
                "bug-report",
                "--agent",
                "gemini-cli",
                "--destination",
                str(project),
                "--apply",
            )
            self.assertEqual(updated.returncode, 0, updated.stderr)
            self.assertTrue((project / ".gemini/skills/bug-report/SKILL.md").is_file())

            manifest = json.loads(
                (project / ".gemini/qacraft/manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["agent"], "gemini-cli")
            self.assertEqual(manifest["skills"], ["bug-report", "feature-qa"])
            self.assertFalse((project / ".agents/qacraft/manifest.json").exists())
            self.assertFalse((project / ".opencode/qacraft/manifest.json").exists())

    def test_uninstall_preserves_other_adapters_and_unrelated_directories(self):
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "project"
            project.mkdir()
            unrelated_empty = project / "docs" / "empty"
            unrelated_empty.mkdir(parents=True)

            copilot = self.install(project, "github-copilot", "feature-qa")
            self.assertEqual(copilot.returncode, 0, copilot.stderr)
            opencode = self.install(project, "opencode", "bug-report")
            self.assertEqual(opencode.returncode, 0, opencode.stderr)

            removed = self.uninstall(project, "github-copilot")
            self.assertEqual(removed.returncode, 0, removed.stderr)

            self.assertFalse((project / ".github/qacraft/manifest.json").exists())
            self.assertFalse((project / ".github/skills/feature-qa/SKILL.md").exists())
            self.assertTrue((project / ".opencode/qacraft/manifest.json").is_file())
            self.assertTrue((project / ".opencode/skills/bug-report/SKILL.md").is_file())
            self.assertTrue(unrelated_empty.is_dir())

    def test_new_adapter_install_refuses_unowned_target_file(self):
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "project"
            conflict = project / ".opencode/skills/feature-qa/SKILL.md"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("keep me", encoding="utf-8")

            result = self.install(project, "opencode", "feature-qa")
            self.assertEqual(result.returncode, 1)
            self.assertIn("already exist", result.stderr)
            self.assertEqual(conflict.read_text(encoding="utf-8"), "keep me")
            self.assertFalse((project / ".opencode/qacraft/manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
