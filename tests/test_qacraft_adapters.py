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
    AGENT_SKILL_TRANSFORM,
    build_file_specs,
    layout_for,
)


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

    def test_verified_adapter_layouts(self):
        codex = layout_for("codex")
        claude = layout_for("claude-code")
        self.assertEqual(codex.skills_root.as_posix(), ".agents/skills")
        self.assertEqual(codex.manifest_path.as_posix(), ".agents/qacraft/manifest.json")
        self.assertEqual(claude.skills_root.as_posix(), ".claude/skills")
        self.assertEqual(claude.manifest_path.as_posix(), ".claude/qacraft/manifest.json")

        codex_specs = build_file_specs(
            "codex",
            ["feature-qa"],
            ["qa-standards.md"],
        )
        self.assertIn(
            {
                "source": "skills/feature-qa/SKILL.md",
                "target": ".agents/skills/feature-qa/SKILL.md",
                "transform": AGENT_SKILL_TRANSFORM,
            },
            codex_specs,
        )
        self.assertIn(
            {
                "source": "shared/qa-standards.md",
                "target": ".agents/qacraft/shared/qa-standards.md",
            },
            codex_specs,
        )

    def test_installed_agent_skill_uses_standard_frontmatter(self):
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "project"
            project.mkdir()
            result = self.install(project, "codex", "feature-qa")
            self.assertEqual(result.returncode, 0, result.stderr)

            source = (ROOT / "skills/feature-qa/SKILL.md").read_text(encoding="utf-8")
            installed_path = project / ".agents/skills/feature-qa/SKILL.md"
            installed = installed_path.read_text(encoding="utf-8")
            frontmatter = installed.split("---", 2)[1]

            self.assertIn('name: "feature-qa"', frontmatter)
            self.assertIn('description: "Turns a ticket', frontmatter)
            self.assertIn("metadata:", frontmatter)
            self.assertIn('qacraft-command: "/feature-qa"', frontmatter)
            self.assertIn('qacraft-version: "1.0.0"', frontmatter)
            self.assertIn('qacraft-status: "specification"', frontmatter)
            self.assertNotIn("\ncommand:", frontmatter)
            self.assertNotIn("\nversion:", frontmatter)
            self.assertNotIn("\nstatus:", frontmatter)

            source_body = source.split("\n---\n", 1)[1]
            installed_body = installed.split("\n---\n", 1)[1]
            self.assertEqual(installed_body, source_body)

            manifest = json.loads(
                (project / ".agents/qacraft/manifest.json").read_text(encoding="utf-8")
            )
            record = next(
                item
                for item in manifest["files"]
                if item["path"] == ".agents/skills/feature-qa/SKILL.md"
            )
            self.assertEqual(record["transform"], AGENT_SKILL_TRANSFORM)
            self.assertNotEqual(record["source_sha256"], record["sha256"])

    def test_codex_and_claude_code_installations_can_coexist(self):
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "project"
            project.mkdir()

            codex_result = self.install(project, "codex", "feature-qa")
            self.assertEqual(codex_result.returncode, 0, codex_result.stderr)
            claude_result = self.install(project, "claude-code", "bug-report")
            self.assertEqual(claude_result.returncode, 0, claude_result.stderr)

            self.assertTrue((project / ".agents/skills/feature-qa/SKILL.md").is_file())
            self.assertTrue((project / ".claude/skills/bug-report/SKILL.md").is_file())
            self.assertTrue((project / ".agents/qacraft/manifest.json").is_file())
            self.assertTrue((project / ".claude/qacraft/manifest.json").is_file())
            self.assertFalse((project / ".qacraft-manifest.json").exists())

            codex_verify = self.run_cli(
                "verify-install",
                "--agent",
                "codex",
                "--destination",
                str(project),
            )
            self.assertEqual(codex_verify.returncode, 0, codex_verify.stderr)
            self.assertEqual(json.loads(codex_verify.stdout)["agent"], "codex")

            claude_verify = self.run_cli(
                "verify-install",
                "--agent",
                "claude-code",
                "--destination",
                str(project),
            )
            self.assertEqual(claude_verify.returncode, 0, claude_verify.stderr)
            self.assertEqual(
                json.loads(claude_verify.stdout)["agent"],
                "claude-code",
            )

    def test_codex_update_uses_codex_manifest_and_layout(self):
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "project"
            project.mkdir()
            installed = self.install(project, "codex", "feature-qa")
            self.assertEqual(installed.returncode, 0, installed.stderr)

            updated = self.run_cli(
                "update",
                "feature-qa",
                "bug-report",
                "--agent",
                "codex",
                "--destination",
                str(project),
                "--apply",
            )
            self.assertEqual(updated.returncode, 0, updated.stderr)
            self.assertTrue((project / ".agents/skills/bug-report/SKILL.md").is_file())

            manifest = json.loads(
                (project / ".agents/qacraft/manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["agent"], "codex")
            self.assertEqual(manifest["skills"], ["bug-report", "feature-qa"])
            self.assertFalse((project / ".claude/qacraft/manifest.json").exists())

    def test_uninstall_preserves_other_adapter_and_unrelated_directories(self):
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "project"
            project.mkdir()
            unrelated_empty = project / "docs" / "empty"
            unrelated_empty.mkdir(parents=True)

            codex_result = self.install(project, "codex", "feature-qa")
            self.assertEqual(codex_result.returncode, 0, codex_result.stderr)
            claude_result = self.install(project, "claude-code", "bug-report")
            self.assertEqual(claude_result.returncode, 0, claude_result.stderr)

            removed = self.run_cli(
                "uninstall",
                "--agent",
                "codex",
                "--destination",
                str(project),
                "--apply",
            )
            self.assertEqual(removed.returncode, 0, removed.stderr)

            self.assertFalse((project / ".agents/qacraft/manifest.json").exists())
            self.assertFalse((project / ".agents/skills/feature-qa/SKILL.md").exists())
            self.assertTrue((project / ".claude/qacraft/manifest.json").is_file())
            self.assertTrue((project / ".claude/skills/bug-report/SKILL.md").is_file())
            self.assertTrue(unrelated_empty.is_dir())

    def test_codex_install_refuses_unowned_target_file(self):
        with tempfile.TemporaryDirectory() as parent:
            project = Path(parent) / "project"
            conflict = project / ".agents/skills/feature-qa/SKILL.md"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("keep me", encoding="utf-8")

            result = self.install(project, "codex", "feature-qa")
            self.assertEqual(result.returncode, 1)
            self.assertIn("already exist", result.stderr)
            self.assertEqual(conflict.read_text(encoding="utf-8"), "keep me")
            self.assertFalse((project / ".agents/qacraft/manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
