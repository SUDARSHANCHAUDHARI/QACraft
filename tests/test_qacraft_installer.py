import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from qacraft_installer import InstallError, build_install_plan  # noqa: E402


class QACraftInstallerSafetyTests(unittest.TestCase):
    def test_rejects_symlink_destination(self):
        with tempfile.TemporaryDirectory() as parent:
            parent_path = Path(parent)
            real = parent_path / "real"
            real.mkdir()
            link = parent_path / "link"
            link.symlink_to(real, target_is_directory=True)

            with self.assertRaisesRegex(InstallError, "symbolic link"):
                build_install_plan(ROOT, link, ["skills/feature-qa/SKILL.md"])

    def test_rejects_symlink_inside_destination_tree(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "destination"
            destination.mkdir()
            outside = Path(parent) / "outside"
            outside.mkdir()
            (destination / "skills").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(InstallError, "symbolic link"):
                build_install_plan(
                    ROOT,
                    destination,
                    ["skills/feature-qa/SKILL.md"],
                )

    def test_rejects_source_parent_traversal(self):
        with tempfile.TemporaryDirectory() as parent:
            destination = Path(parent) / "destination"
            with self.assertRaisesRegex(InstallError, "Unsafe source path"):
                build_install_plan(ROOT, destination, ["../outside.txt"])


if __name__ == "__main__":
    unittest.main()
