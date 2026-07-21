import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_generator():
    path = ROOT / "scripts" / "generate_docs.py"
    spec = importlib.util.spec_from_file_location("qa_generate_docs", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class RepositoryTests(unittest.TestCase):
    def test_repository_validator(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_repo.py")],
            cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_catalog_has_unique_commands(self):
        data = json.loads((ROOT / "catalog" / "skills.json").read_text(encoding="utf-8"))
        commands = [s["command"] for s in data["skills"]]
        self.assertEqual(len(commands), 25)
        self.assertEqual(len(commands), len(set(commands)))

    def test_renderer_escapes_malicious_values(self):
        generator = load_generator()
        corpus = json.loads((ROOT / "tests" / "malicious-input-corpus.json").read_text(encoding="utf-8"))
        for item in corpus:
            raw = item["value"]
            if raw == "__GENERATE_LONG_TITLE_4096__":
                raw = "A" * 4096
            escaped = generator.esc(raw)
            if "<" in raw:
                self.assertNotIn("<script", escaped.lower())
                self.assertNotIn("<img", escaped.lower())
            self.assertNotEqual(raw, escaped) if any(ch in raw for ch in "<>&\"") else None

    def test_every_skill_has_eight_phases(self):
        data = json.loads((ROOT / "catalog" / "skills.json").read_text(encoding="utf-8"))
        for skill in data["skills"]:
            self.assertEqual(len(skill["phases"]), 8, skill["slug"])

if __name__ == "__main__":
    unittest.main()
