#!/usr/bin/env python3
"""Retry only the false-negative QACraft 1.4.1 public checks."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

VERSION = "1.4.1"
REPOSITORY = "SUDARSHANCHAUDHARI/QACraft"
DOCS_ROOT = "https://sudarshanchaudhari.github.io/QACraft/"
REPORT = Path(os.environ.get("QACRAFT_PUBLIC_REPORT", "QACRAFT_V1.4.1_PUBLIC_VALIDATION_RETRY.md"))
RESULTS: list[tuple[str, bool, str]] = []


def get(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "QACraft-public-release-validation-retry/1.4.1"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} for {url}")
        return response.read()


def record(area: str, passed: bool, detail: str) -> None:
    RESULTS.append((area, passed, detail))
    print(f"[{'PASS' if passed else 'FAIL'}] {area}: {detail}")


def run(command: list[str | Path], expected: int | set[int] = 0) -> subprocess.CompletedProcess[str]:
    args = [str(item) for item in command]
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    expected_codes = {expected} if isinstance(expected, int) else expected
    if result.returncode not in expected_codes:
        raise RuntimeError(
            f"Command returned {result.returncode}: {' '.join(args)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def create_venv(path: Path) -> tuple[Path, Path]:
    run([sys.executable, "-m", "venv", path])
    python = path / "bin/python"
    qacraft = path / "bin/qacraft"
    run([python, "-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "pip"])
    return python, qacraft


def validate_wheel(source: str, url: str, root: Path) -> None:
    wheel_dir = root / source
    wheel_dir.mkdir()
    wheel = wheel_dir / f"qacraft-{VERSION}-py3-none-any.whl"
    content = get(url)
    wheel.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()

    python, qacraft = create_venv(root / f"venv-{source}")
    run([python, "-m", "pip", "install", "--disable-pip-version-check", "--no-deps", wheel])
    show = run([python, "-m", "pip", "show", "qacraft"])
    if f"Version: {VERSION}" not in show.stdout:
        raise RuntimeError(show.stdout)
    run([qacraft, "doctor"])
    release_check = json.loads(run([qacraft, "release-check", "--json"]).stdout)
    if release_check.get("version") != VERSION or not release_check.get("passed"):
        raise RuntimeError(json.dumps(release_check))

    parent = root / f"missing-{source}"
    parent.mkdir()
    missing = parent / "project"
    for apply in (False, True):
        command: list[str | Path] = [
            qacraft,
            "install",
            "feature-qa",
            "--agent",
            "codex",
            "--destination",
            missing,
        ]
        if apply:
            command.append("--apply")
        result = run(command, expected={1, 2})
        if "does not exist" not in (result.stdout + result.stderr).lower():
            raise RuntimeError("Controlled missing-destination message was absent")
        if missing.exists():
            raise RuntimeError("Missing destination was created")

    record(f"Wheel installation: {source}", True, f"digest={digest}; doctor, release-check, and destination safety passed")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="qacraft-public-retry-") as temp:
        root = Path(temp)
        release = json.loads(
            get(f"https://api.github.com/repos/{REPOSITORY}/releases/tags/v{VERSION}").decode("utf-8")
        )
        pypi = json.loads(get(f"https://pypi.org/pypi/qacraft/{VERSION}/json").decode("utf-8"))
        github_assets = {item["name"]: item["browser_download_url"] for item in release["assets"]}
        pypi_assets = {item["filename"]: item["url"] for item in pypi["urls"]}
        wheel_name = f"qacraft-{VERSION}-py3-none-any.whl"

        for source, url in (
            ("github", github_assets[wheel_name]),
            ("pypi", pypi_assets[wheel_name]),
        ):
            try:
                validate_wheel(source, url, root)
            except Exception as exc:
                record(f"Wheel installation: {source}", False, str(exc))

        pages = {
            "Installation documentation": "INSTALLATION/",
            "Compatibility documentation": "COMPATIBILITY/",
            "Evaluations documentation": "EVALUATIONS/",
            "Production readiness documentation": "PRODUCTION_READINESS/",
            "Publishing documentation": "PUBLISHING/",
            "Release checklist documentation": "RELEASE_CHECKLIST/",
        }
        for area, relative in pages.items():
            try:
                body = get(DOCS_ROOT + relative).decode("utf-8", errors="replace")
                valid = len(body) > 500
                if area == "Installation documentation":
                    valid = valid and "must already exist" in body.lower() and VERSION in body
                record(area, valid, f"HTTP 200, bytes={len(body)}, path={relative}")
            except Exception as exc:
                record(area, False, str(exc))

    passed = sum(passed for _, passed, _ in RESULTS)
    failed = len(RESULTS) - passed
    recommendation = "APPROVED FOR PUBLIC SHARING" if failed == 0 else "NOT APPROVED FOR PUBLIC SHARING"
    lines = [
        f"# QACraft v{VERSION} Public Validation Retry",
        "",
        f"- Result: {'PASS' if failed == 0 else 'FAIL'}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        f"- Recommendation: {recommendation}",
        "",
        "| Area | Result | Detail |",
        "|---|---|---|",
    ]
    for area, ok, detail in RESULTS:
        lines.append(f"| {area} | {'PASS' if ok else 'FAIL'} | {detail.replace('|', '/').replace(chr(10), ' ')} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Public-sharing recommendation: {recommendation}")
    print(f"Report path: {REPORT}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
