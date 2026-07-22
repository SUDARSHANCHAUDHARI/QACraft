#!/usr/bin/env python3
"""Run a local, side-effect-contained QACraft production-readiness demo."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "qacraft.py"
EXAMPLE = ROOT / "evaluations" / "examples" / "feature-qa-pass.json"


class DemoError(RuntimeError):
    """Raised when an end-to-end demo step fails."""


def run(*args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != expected:
        raise DemoError(
            f"Command failed ({result.returncode}, expected {expected}): "
            f"qacraft {' '.join(args)}\n{result.stdout}\n{result.stderr}"
        )
    return result


def main() -> int:
    run("doctor")
    run("eval-list")
    evaluation = json.loads(run("evaluate", "--input", str(EXAMPLE)).stdout)
    if not evaluation.get("passed"):
        raise DemoError("Passing evaluation fixture did not pass.")

    with tempfile.TemporaryDirectory(prefix="qacraft-demo-") as parent:
        project = Path(parent) / "project"
        project.mkdir()
        unrelated = project / "keep-me.txt"
        unrelated.write_text("unrelated project file\n", encoding="utf-8")

        preview = json.loads(
            run(
                "install",
                "feature-qa",
                "--agent",
                "codex",
                "--destination",
                str(project),
            ).stdout
        )
        if preview.get("writes_performed") is not False:
            raise DemoError("Install preview unexpectedly performed writes.")

        run(
            "install",
            "feature-qa",
            "--agent",
            "codex",
            "--destination",
            str(project),
            "--apply",
        )
        run("verify-install", "--agent", "codex", "--destination", str(project))

        run(
            "update",
            "feature-qa",
            "bug-report",
            "--agent",
            "codex",
            "--destination",
            str(project),
            "--apply",
        )
        run("verify-install", "--agent", "codex", "--destination", str(project))

        uninstall_preview = json.loads(
            run("uninstall", "--agent", "codex", "--destination", str(project)).stdout
        )
        if uninstall_preview.get("writes_performed") is not False:
            raise DemoError("Uninstall preview unexpectedly performed writes.")

        run(
            "uninstall",
            "--agent",
            "codex",
            "--destination",
            str(project),
            "--apply",
        )
        if not unrelated.is_file():
            raise DemoError("Unrelated project file was removed.")
        if (project / ".agents/qacraft/manifest.json").exists():
            raise DemoError("Adapter manifest remains after uninstall.")

    print("QACraft end-to-end demo passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DemoError as exc:
        print(f"Demo failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
