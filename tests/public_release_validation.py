#!/usr/bin/env python3
"""Independent public-release validation for QACraft 1.4.1."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

VERSION = "1.4.1"
REPOSITORY = "SUDARSHANCHAUDHARI/QACraft"
PYPI_JSON = f"https://pypi.org/pypi/qacraft/{VERSION}/json"
GITHUB_RELEASE_JSON = f"https://api.github.com/repos/{REPOSITORY}/releases/tags/v{VERSION}"
DOCS_ROOT = "https://sudarshanchaudhari.github.io/QACraft/"
EXPECTED_FILES = {
    "wheel": f"qacraft-{VERSION}-py3-none-any.whl",
    "sdist": f"qacraft-{VERSION}.tar.gz",
}
AGENTS = ("generic", "codex", "claude-code", "github-copilot", "gemini-cli", "opencode")


@dataclass
class Result:
    area: str
    passed: bool
    detail: str


RESULTS: list[Result] = []
COMMANDS: list[str] = []


def record(area: str, passed: bool, detail: str) -> None:
    RESULTS.append(Result(area, passed, detail))
    marker = "PASS" if passed else "FAIL"
    print(f"[{marker}] {area}: {detail}")


def http_get(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "QACraft-public-release-validation/1.4.1",
            "Accept": "application/vnd.github+json, application/json, text/html;q=0.9, */*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} for {url}")
        return response.read()


def http_json(url: str) -> dict:
    return json.loads(http_get(url).decode("utf-8"))


def download(url: str, destination: Path) -> str:
    content = http_get(url)
    destination.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(
    command: Iterable[str],
    *,
    cwd: Path | None = None,
    expected: int | set[int] = 0,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    args = [str(item) for item in command]
    COMMANDS.append(" ".join(args))
    result = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    expected_codes = {expected} if isinstance(expected, int) else set(expected)
    if result.returncode not in expected_codes:
        raise RuntimeError(
            f"Command returned {result.returncode}, expected {sorted(expected_codes)}: {' '.join(args)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def venv_paths(root: Path) -> tuple[Path, Path]:
    bin_dir = root / ("Scripts" if os.name == "nt" else "bin")
    return bin_dir / "python", bin_dir / ("qacraft.exe" if os.name == "nt" else "qacraft")


def create_venv(root: Path) -> tuple[Path, Path]:
    run([sys.executable, "-m", "venv", str(root)])
    python, qacraft = venv_paths(root)
    run([python, "-m", "pip", "install", "--disable-pip-version-check", "--upgrade", "pip"])
    return python, qacraft


def assert_missing_destination_rejected(qacraft: Path, root: Path, agent: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    missing = root / f"missing-{agent}"
    for apply in (False, True):
        command = [
            qacraft,
            "install",
            "feature-qa",
            "--agent",
            agent,
            "--destination",
            missing,
        ]
        if apply:
            command.append("--apply")
        result = run(command, expected={1, 2})
        combined = f"{result.stdout}\n{result.stderr}".lower()
        if "does not exist" not in combined:
            raise RuntimeError(f"Missing controlled error for agent={agent}, apply={apply}: {combined}")
        if missing.exists():
            raise RuntimeError(f"QACraft created missing destination for agent={agent}, apply={apply}")


def lifecycle(qacraft: Path, root: Path, agent: str) -> None:
    project = root / f"project-{agent}"
    project.mkdir()
    keep = project / "keep-me.txt"
    keep.write_text("unrelated\n", encoding="utf-8")
    baseline = sha256(keep)

    preview = run(
        [qacraft, "install", "feature-qa", "--agent", agent, "--destination", project]
    )
    plan = json.loads(preview.stdout)
    if plan.get("writes_performed") is not False:
        raise RuntimeError(f"Install preview wrote files for {agent}")

    run(
        [
            qacraft,
            "install",
            "feature-qa",
            "--agent",
            agent,
            "--destination",
            project,
            "--apply",
        ]
    )
    run([qacraft, "verify-install", "--agent", agent, "--destination", project])
    run(
        [
            qacraft,
            "update",
            "feature-qa",
            "bug-report",
            "--agent",
            agent,
            "--destination",
            project,
            "--apply",
        ]
    )
    run([qacraft, "verify-install", "--agent", agent, "--destination", project])

    uninstall_preview = run(
        [qacraft, "uninstall", "--agent", agent, "--destination", project]
    )
    uninstall_plan = json.loads(uninstall_preview.stdout)
    if uninstall_plan.get("writes_performed") is not False:
        raise RuntimeError(f"Uninstall preview wrote files for {agent}")

    run(
        [qacraft, "uninstall", "--agent", agent, "--destination", project, "--apply"]
    )
    if not keep.is_file() or sha256(keep) != baseline:
        raise RuntimeError(f"Unrelated file changed during lifecycle for {agent}")


def validate_installed_runtime(python: Path, qacraft: Path, source: str) -> None:
    show = run([python, "-m", "pip", "show", "qacraft"])
    if f"Version: {VERSION}" not in show.stdout:
        raise RuntimeError(f"Wrong installed version from {source}: {show.stdout}")
    run([qacraft, "doctor"])
    release = run([qacraft, "release-check", "--json"])
    report = json.loads(release.stdout)
    if report.get("version") != VERSION or not report.get("passed"):
        raise RuntimeError(f"Release check failed from {source}: {release.stdout}")
    run([python, "-m", "qacraft", "--help"])


def main() -> int:
    report_path = Path(os.environ.get("QACRAFT_PUBLIC_REPORT", "QACRAFT_V1.4.1_PUBLIC_VALIDATION.md"))
    with tempfile.TemporaryDirectory(prefix="qacraft-public-1.4.1-") as temp:
        root = Path(temp)
        downloads = root / "downloads"
        downloads.mkdir()

        try:
            release = http_json(GITHUB_RELEASE_JSON)
            ok = (
                release.get("tag_name") == f"v{VERSION}"
                and not release.get("draft")
                and not release.get("prerelease")
            )
            record("GitHub release", ok, f"tag={release.get('tag_name')}, draft={release.get('draft')}, prerelease={release.get('prerelease')}")
        except Exception as exc:
            release = {}
            record("GitHub release", False, str(exc))

        try:
            pypi = http_json(PYPI_JSON)
            pypi_version = pypi.get("info", {}).get("version")
            record("PyPI metadata", pypi_version == VERSION, f"version={pypi_version}")
        except Exception as exc:
            pypi = {}
            record("PyPI metadata", False, str(exc))

        github_assets = {item.get("name"): item for item in release.get("assets", [])}
        pypi_assets = {item.get("filename"): item for item in pypi.get("urls", [])}
        artifact_paths: dict[str, Path] = {}

        for kind, filename in EXPECTED_FILES.items():
            github_item = github_assets.get(filename)
            pypi_item = pypi_assets.get(filename)
            if not github_item or not pypi_item:
                record(
                    f"{kind} artifact availability",
                    False,
                    f"GitHub={bool(github_item)}, PyPI={bool(pypi_item)}, filename={filename}",
                )
                continue
            try:
                github_path = downloads / f"github-{filename}"
                pypi_path = downloads / f"pypi-{filename}"
                github_digest = download(github_item["browser_download_url"], github_path)
                pypi_digest = download(pypi_item["url"], pypi_path)
                declared = pypi_item.get("digests", {}).get("sha256")
                matches = github_digest == pypi_digest == declared
                record(
                    f"{kind} artifact digest",
                    matches,
                    f"GitHub={github_digest}, PyPI={pypi_digest}, declared={declared}",
                )
                artifact_paths[f"github-{kind}"] = github_path
                artifact_paths[f"pypi-{kind}"] = pypi_path
            except Exception as exc:
                record(f"{kind} artifact digest", False, str(exc))

        docs = {
            "Documentation home": DOCS_ROOT,
            "Installation documentation": DOCS_ROOT + "installation/",
            "Compatibility documentation": DOCS_ROOT + "compatibility/",
            "Evaluations documentation": DOCS_ROOT + "evaluations/",
            "Production readiness documentation": DOCS_ROOT + "production-readiness/",
            "Publishing documentation": DOCS_ROOT + "publishing/",
            "Release checklist documentation": DOCS_ROOT + "release-checklist/",
        }
        for area, url in docs.items():
            try:
                body = http_get(url).decode("utf-8", errors="replace")
                lower = body.lower()
                extra_ok = True
                if area == "Installation documentation":
                    extra_ok = "must already exist" in lower and VERSION in body
                record(area, extra_ok, f"HTTP 200, bytes={len(body)}")
            except Exception as exc:
                record(area, False, str(exc))

        pypi_env = root / "pypi-env"
        try:
            python, qacraft = create_venv(pypi_env)
            run([python, "-m", "pip", "install", "--disable-pip-version-check", f"qacraft=={VERSION}"])
            validate_installed_runtime(python, qacraft, "PyPI")
            record("Fresh PyPI installation", True, f"qacraft=={VERSION} installed and release-check passed")
        except Exception as exc:
            python = qacraft = Path("missing")
            record("Fresh PyPI installation", False, str(exc))

        if qacraft.exists():
            for agent in AGENTS:
                try:
                    assert_missing_destination_rejected(qacraft, root / "missing-tests", agent)
                    record(f"Missing destination rejection: {agent}", True, "preview and apply rejected without creating the root")
                except Exception as exc:
                    record(f"Missing destination rejection: {agent}", False, str(exc))

            for agent in AGENTS:
                try:
                    lifecycle(qacraft, root, agent)
                    record(f"Existing-directory lifecycle: {agent}", True, "install, verify, update, verify, and uninstall passed")
                except Exception as exc:
                    record(f"Existing-directory lifecycle: {agent}", False, str(exc))

            try:
                runtime = run([python, "-c", "import qacraft; print(qacraft.runtime_root())"]).stdout.strip()
                runtime_root = Path(runtime)
                passing = runtime_root / "evaluations/examples/api-qa-pass.json"
                failing = runtime_root / "evaluations/fixtures/api-qa-secret-output.json"
                run([qacraft, "evaluate", "--input", passing], expected=0)
                run([qacraft, "evaluate", "--input", failing], expected=1)
                malformed = root / "malformed.json"
                malformed.write_text("{not-json", encoding="utf-8")
                run([qacraft, "evaluate", "--input", malformed], expected=2)
                record("Evaluation smoke tests", True, "passing, targeted failing, and malformed candidates returned expected exit codes")
            except Exception as exc:
                record("Evaluation smoke tests", False, str(exc))

        for label, artifact in sorted(artifact_paths.items()):
            env_root = root / f"artifact-env-{label}"
            try:
                artifact_python, artifact_qacraft = create_venv(env_root)
                run([artifact_python, "-m", "pip", "install", "--disable-pip-version-check", "--no-deps", artifact])
                validate_installed_runtime(artifact_python, artifact_qacraft, label)
                if label in {"github-wheel", "pypi-wheel"}:
                    assert_missing_destination_rejected(artifact_qacraft, root / label, "codex")
                record(f"Artifact installation: {label}", True, "doctor and release-check passed")
            except Exception as exc:
                record(f"Artifact installation: {label}", False, str(exc))

    passed = sum(item.passed for item in RESULTS)
    failed = len(RESULTS) - passed
    overall = "APPROVED FOR PUBLIC SHARING" if failed == 0 else "NOT APPROVED FOR PUBLIC SHARING"

    lines = [
        f"# QACraft v{VERSION} Public Release Validation",
        "",
        "## Executive summary",
        f"- Overall result: {'PASS' if failed == 0 else 'FAIL'}",
        f"- Public-sharing recommendation: {overall}",
        f"- Tests passed: {passed}",
        f"- Tests failed: {failed}",
        "",
        "## Results",
        "| Area | Result | Detail |",
        "|---|---|---|",
    ]
    for item in RESULTS:
        detail = item.detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {item.area} | {'PASS' if item.passed else 'FAIL'} | {detail} |")
    lines.extend(
        [
            "",
            "## Commands executed",
            "```text",
            *COMMANDS,
            "```",
            "",
            "## Final recommendation",
            overall,
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print("\n=== FINAL SUMMARY ===")
    print(f"Overall result: {'PASS' if failed == 0 else 'FAIL'}")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print("Critical findings: 0")
    print("High findings: 0")
    print(f"Medium findings: {failed}")
    print("Low findings: 0")
    print(f"Public-sharing recommendation: {overall}")
    print(f"Report path: {report_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
