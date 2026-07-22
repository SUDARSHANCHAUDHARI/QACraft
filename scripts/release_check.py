#!/usr/bin/env python3
"""Deterministic production-readiness checks for a QACraft release."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from qacraft_eval import EvaluationError, evaluate_file, load_rubrics

PRIORITY_SKILLS = (
    "feature-qa",
    "ticket-review",
    "bug-report",
    "verify-fix",
    "release-qa",
)
REQUIRED_RELEASE_FILES = (
    "README.md",
    "CHANGELOG.md",
    "RELEASE_CHECKLIST.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "docs/INSTALLATION.md",
    "docs/COMPATIBILITY.md",
    "docs/DEMO.md",
    "docs/EVALUATIONS.md",
    "docs/PRODUCTION_READINESS.md",
    "evaluations/rubrics.json",
    "evaluations/examples/feature-qa-pass.json",
    "schemas/evaluation-candidate.schema.json",
    "schemas/evaluation-report.schema.json",
)


class ReleaseCheckError(RuntimeError):
    """Raised when release metadata cannot be inspected."""


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReleaseCheckError(f"Cannot read {path}: {exc}") from exc


def _version(root: Path) -> str:
    match = re.search(
        r'^version\s*=\s*"([^"]+)"',
        _read(root / "pyproject.toml"),
        flags=re.MULTILINE,
    )
    if not match:
        raise ReleaseCheckError("Cannot determine version from pyproject.toml.")
    return match.group(1)


def _section(text: str, heading: str) -> str:
    marker = f"\n{heading}\n"
    padded = f"\n{text}"
    start = padded.find(marker)
    if start < 0:
        return ""
    content_start = start + len(marker)
    next_heading = padded.find("\n## ", content_start)
    return padded[content_start:] if next_heading < 0 else padded[content_start:next_heading]


def _skill_contract(path: Path) -> dict[str, list[str]]:
    text = _read(path)
    gates = re.findall(
        r"^- \*\*Gate \d+:\*\* (.+)$",
        _section(text, "## Approval gates"),
        flags=re.MULTILINE,
    )
    outputs = re.findall(
        r"^- `([^`]+)`$",
        _section(text, "## Output contract"),
        flags=re.MULTILINE,
    )
    result_states = re.findall(
        r"^- \*\*([^*]+)\*\*:",
        _section(text, "## Result states"),
        flags=re.MULTILINE,
    )
    ordered_decisions = re.findall(
        r"^\d+\. \*\*([^*]+)\*\*:",
        _section(text, "## Ordered decision policy"),
        flags=re.MULTILINE,
    )
    return {
        "gates": gates,
        "outputs": outputs,
        "decisions": list(dict.fromkeys(result_states + ordered_decisions)),
    }


def _check(checks: list[dict], check_id: str, passed: bool, detail: str) -> None:
    checks.append({"id": check_id, "passed": passed, "detail": detail})


def run_release_checks(root: Path) -> dict:
    root = root.resolve(strict=True)
    version = _version(root)
    checks: list[dict] = []

    missing_files = [
        relative for relative in REQUIRED_RELEASE_FILES if not (root / relative).is_file()
    ]
    _check(
        checks,
        "release_files",
        not missing_files,
        "All required release files exist."
        if not missing_files
        else f"Missing release files: {missing_files}",
    )

    changelog = _read(root / "CHANGELOG.md") if (root / "CHANGELOG.md").is_file() else ""
    changelog_pattern = rf"^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$"
    changelog_ok = bool(re.search(changelog_pattern, changelog, flags=re.MULTILINE))
    _check(
        checks,
        "versioned_changelog",
        changelog_ok,
        f"CHANGELOG contains release {version}."
        if changelog_ok
        else f"CHANGELOG is missing a dated {version} section.",
    )

    readme = _read(root / "README.md")
    readme_tokens = (
        "scripts/qacraft.py install",
        "scripts/qacraft.py verify-install",
        "scripts/qacraft.py update",
        "scripts/qacraft.py uninstall",
        "scripts/qacraft.py evaluate",
        "docs/INSTALLATION.md",
        "docs/COMPATIBILITY.md",
        "docs/DEMO.md",
    )
    missing_readme = [token for token in readme_tokens if token not in readme]
    _check(
        checks,
        "readme_quickstart",
        not missing_readme,
        "README documents install, lifecycle, evaluation, and release guides."
        if not missing_readme
        else f"README is missing: {missing_readme}",
    )

    workflow = _read(root / ".github" / "workflows" / "validate.yml")
    workflow_ok = (
        "pull_request:" in workflow
        and "workflow_dispatch:" in workflow
        and "\n  push:" not in workflow
        and workflow.count("runs-on:") == 1
        and 'python-version: "3.12"' in workflow
    )
    _check(
        checks,
        "lean_ci",
        workflow_ok,
        "CI is PR/manual only with one Python 3.12 job."
        if workflow_ok
        else "CI must remain PR/manual only with exactly one Python 3.12 job.",
    )

    rubric_path = root / "evaluations" / "rubrics.json"
    try:
        rubrics = load_rubrics(rubric_path)
    except EvaluationError as exc:
        rubrics = {}
        rubric_error = str(exc)
    else:
        rubric_error = ""

    coverage_ok = set(rubrics) == set(PRIORITY_SKILLS)
    _check(
        checks,
        "rubric_coverage",
        coverage_ok,
        "Rubrics cover exactly the five priority skills."
        if coverage_ok
        else f"Rubric coverage mismatch: {sorted(rubrics)} {rubric_error}".strip(),
    )

    contract_errors: list[str] = []
    for skill in PRIORITY_SKILLS:
        rubric = rubrics.get(skill)
        if not rubric:
            continue
        contract = _skill_contract(root / "skills" / skill / "SKILL.md")
        if rubric.get("required_gates") != contract["gates"]:
            contract_errors.append(f"{skill}: approval gates differ from SKILL.md")
        if rubric.get("required_outputs") != contract["outputs"]:
            contract_errors.append(f"{skill}: required outputs differ from SKILL.md")
        unknown_decisions = sorted(
            set(rubric.get("allowed_decisions", [])) - set(contract["decisions"])
        )
        if unknown_decisions:
            contract_errors.append(
                f"{skill}: decisions not present in SKILL.md: {unknown_decisions}"
            )
    _check(
        checks,
        "rubric_skill_binding",
        not contract_errors,
        "Every rubric is bound to its canonical skill gates, decisions, and outputs."
        if not contract_errors
        else "; ".join(contract_errors),
    )

    example_path = root / "evaluations" / "examples" / "feature-qa-pass.json"
    try:
        example_report = evaluate_file(example_path, rubric_path)
    except EvaluationError as exc:
        example_ok = False
        example_detail = f"Passing example could not be evaluated: {exc}"
    else:
        example_ok = example_report["passed"]
        example_detail = (
            "The published feature-qa example passes all behavior checks."
            if example_ok
            else f"Published example failed: {example_report['summary']['failed_checks']}"
        )
    _check(checks, "published_example", example_ok, example_detail)

    metadata = _read(root / "pyproject.toml")
    metadata_ok = (
        'readme = "README.md"' in metadata
        and 'license = { text = "MIT" }' in metadata
        and "[project.urls]" in metadata
    )
    _check(
        checks,
        "project_metadata",
        metadata_ok,
        "Project metadata includes README, license, and repository URLs."
        if metadata_ok
        else "pyproject.toml is missing release metadata.",
    )

    failed = [item["id"] for item in checks if not item["passed"]]
    return {
        "schema_version": "1.0.0",
        "version": version,
        "passed": not failed,
        "checks": checks,
        "summary": {
            "check_count": len(checks),
            "passed_count": len(checks) - len(failed),
            "failed_count": len(failed),
            "failed_checks": failed,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check QACraft release readiness.")
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Repository root",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args(argv)

    try:
        report = run_release_checks(Path(args.root))
    except ReleaseCheckError as exc:
        print(f"Release check failed: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for item in report["checks"]:
            marker = "PASS" if item["passed"] else "FAIL"
            print(f"[{marker}] {item['id']}: {item['detail']}")
        print(
            f"Release {report['version']}: "
            f"{report['summary']['passed_count']}/{report['summary']['check_count']} checks passed."
        )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
