import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "scripts" / "demo.py"


class QACraftDemoTests(unittest.TestCase):
    def test_end_to_end_demo(self):
        result = subprocess.run(
            [sys.executable, str(DEMO)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("QACraft end-to-end demo passed.", result.stdout)


if __name__ == "__main__":
    unittest.main()
