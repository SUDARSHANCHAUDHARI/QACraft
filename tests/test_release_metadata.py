import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class QACraftReleaseMetadataTests(unittest.TestCase):
    def test_version_matches_changelog(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        version = match.group(1)
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## {version} —", changelog)

    def test_production_documentation_exists(self):
        required = [
            "docs/INSTALLATION.md",
            "docs/COMPATIBILITY.md",
            "docs/EVALUATIONS.md",
            "docs/PHASE_2.md",
            "docs/RELEASE_CHECKLIST.md",
            "CHANGELOG.md",
            "scripts/demo.py",
        ]
        for relative in required:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_readme_links_to_release_guides(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for relative in (
            "docs/INSTALLATION.md",
            "docs/COMPATIBILITY.md",
            "docs/EVALUATIONS.md",
            "docs/RELEASE_CHECKLIST.md",
            "CHANGELOG.md",
        ):
            with self.subTest(path=relative):
                self.assertIn(relative, readme)

    def test_phase_two_is_marked_complete(self):
        phase_two = (ROOT / "docs/PHASE_2.md").read_text(encoding="utf-8")
        self.assertIn("Phase 2 is complete.", phase_two)
        self.assertNotIn("Next slice", phase_two)


if __name__ == "__main__":
    unittest.main()
