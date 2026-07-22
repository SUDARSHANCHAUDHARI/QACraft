import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from qacraft_installer import apply_install_plan, build_install_plan  # noqa: E402
from qacraft_uninstaller import (  # noqa: E402
    InstallError,
    apply_uninstall_plan,
    build_uninstall_plan,
)


class QACraftUninstallerTests(unittest.TestCase):
    def install_fixture(self, destination: Path) -> None:
        sources = ["skills/feature-qa/SKILL.md", "shared/qa-standards.md"]
        plan = build_install_plan(ROOT, destination, sources)
        apply_install_plan(plan, qacraft_version="1.0.0", agent="generic", skills=["feature-qa"])

    def test_preview_performs_no_writes(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_fixture(destination)
            plan = build_uninstall_plan(destination)
            self.assertEqual(plan["mode"], "preview-only")
            self.assertFalse(plan["writes_performed"])
            self.assertTrue((destination / "skills/feature-qa/SKILL.md").exists())

    def test_apply_removes_installed_files_and_manifest(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_fixture(destination)
            result = apply_uninstall_plan(build_uninstall_plan(destination))
            self.assertEqual(result["mode"], "applied")
            self.assertTrue(result["writes_performed"])
            self.assertFalse(destination.exists())

    def test_preserves_unrelated_files(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_fixture(destination)
            unrelated = destination / "notes.txt"
            unrelated.write_text("keep me", encoding="utf-8")
            apply_uninstall_plan(build_uninstall_plan(destination))
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep me")
            self.assertFalse((destination / ".qacraft-manifest.json").exists())

    def test_refuses_modified_installed_file(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            self.install_fixture(destination)
            target = destination / "skills/feature-qa/SKILL.md"
            target.write_text("changed", encoding="utf-8")
            plan = build_uninstall_plan(destination)
            self.assertTrue(plan["conflicts"])
            with self.assertRaisesRegex(InstallError, "changed"):
                apply_uninstall_plan(plan)
            self.assertTrue(target.exists())

    def test_rejects_missing_manifest(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            destination.mkdir()
            with self.assertRaisesRegex(InstallError, "Missing valid"):
                build_uninstall_plan(destination)

    def test_rejects_manifest_parent_traversal(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "installed"
            destination.mkdir()
            manifest = {
                "schema_version": 1,
                "files": [{"path": "../outside.txt", "sha256": "x"}],
            }
            (destination / ".qacraft-manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            with self.assertRaisesRegex(InstallError, "Unsafe manifest path"):
                build_uninstall_plan(destination)


if __name__ == "__main__":
    unittest.main()
