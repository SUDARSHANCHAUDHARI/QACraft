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
    "test-plan",
    "regression-scope",
    "customer-issue-repro",
    "api-qa",
    "staged-rollout-check",
)

PUBLISHED_PASS_SKILLS = (
    "feature-qa",
    "test-plan",
    "regression-scope",
    "customer-issue-repro",
    "api-qa",
    "staged-rollout-check",
)

TARGETED_FAILURE_SKILLS = (
    "test-plan",
    "regression-scope",
    "customer-issue-repro",
    "api-qa",
    "staged-rollout-check",
)

REQUIRED_RELEASE_FILES = (
    "README.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "MANIFEST.in",
    "setup.py",
    "qacraft_build.py",
    "qacraft/__init__.py",
    "qacraft/__main__.py",
    "docs/INSTALLATION.md",
    "docs/COMPATIBILITY.md",
    "docs/EVALUATIONS.md",
    "docs/PHASE_2.md",
    "docs/PRODUCTION_READINESS.md",
    "docs/RELEASE_CHECKLIST.md",
    "scripts/demo.py",
    "evaluations/rubrics.json",
    "evaluations/fixtures.json",
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


def _load_json(path: Path) -> object:
    try:
        return json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise ReleaseCheckError(f"Cannot parse JSON from {path}: {exc}") from exc


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


def _safe_fixture_path(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def _validate_published_fixtures(
    root: Path,
    rubric_path: Path,
    rubrics: dict[str, dict],
) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "evaluations" / "fixtures.json"
    try:
        manifest = _load_json(manifest_path)
    except ReleaseCheckError as exc:
        return [str(exc)]

    if not isinstance(manifest, dict):
        return ["Fixture catalog must be a JSON object."]
    if manifest.get("schema_version") != "1.0.0":
        errors.append("Fixture catalog schema_version must be 1.0.0.")

    entries = manifest.get("fixtures")
    if not isinstance(entries, list) or not entries:
        return errors + ["Fixture catalog must define a non-empty fixtures list."]

    seen_paths: set[str] = set()
    passing_skills: set[str] = set()
    failing_skills: set[str] = set()

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"Fixture entry {index} must be an object.")
            continue

        relative = entry.get("path")
        skill = entry.get("skill")
        expected_pass = entry.get("expected_pass")
        expected_failed = entry.get("expected_failed_checks", [])

        if not _safe_fixture_path(relative):
            errors.append(f"Fixture entry {index} has an unsafe path.")
            continue
        if relative in seen_paths:
            errors.append(f"Duplicate fixture path: {relative}")
            continue
        seen_paths.add(relative)

        if skill not in rubrics:
            errors.append(f"Fixture {relative} references unknown skill: {skill}")
            continue
        if not isinstance(expected_pass, bool):
            errors.append(f"Fixture {relative} expected_pass must be boolean.")
            continue
        if not isinstance(expected_failed, list) or not all(
            isinstance(item, str) and item for item in expected_failed
        ):
            errors.append(
                f"Fixture {relative} expected_failed_checks must contain strings."
            )
            continue

        fixture_path = root / "evaluations" / relative
        try:
            report = evaluate_file(fixture_path, rubric_path, skill=skill)
        except EvaluationError as exc:
            errors.append(f"Fixture {relative} could not be evaluated: {exc}")
            continue

        if report["passed"] != expected_pass:
            errors.append(
                f"Fixture {relative} expected passed={expected_pass}, "
                f"received passed={report['passed']}."
            )
            continue

        if expected_pass:
            passing_skills.add(skill)
        else:
            failing_skills.add(skill)
            failed_checks = set(report["summary"]["failed_checks"])
            missing = sorted(set(expected_failed) - failed_checks)
            if missing:
                errors.append(
                    f"Fixture {relative} did not fail expected checks: {missing}"
                )

    missing_pass = sorted(set(PUBLISHED_PASS_SKILLS) - passing_skills)
    if missing_pass:
        errors.append(f"Missing passing fixtures for skills: {missing_pass}")

    missing_failure = sorted(set(TARGETED_FAILURE_SKILLS) - failing_skills)
    if missing_failure:
        errors.append(f"Missing targeted failure fixtures for skills: {missing_failure}")

    return errors


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

    changelog_path = root / "CHANGELOG.md"
    changelog = _read(changelog_path) if changelog_path.is_file() else ""
    changelog_patterns = (
        rf"^## {re.escape(version)} — \d{{4}}-\d{{2}}-\d{{2}}$",
        rf"^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$",
    )
    changelog_ok = any(
        re.search(pattern, changelog, flags=re.MULTILINE)
        for pattern in changelog_patterns
    )
    _check(
        checks,
        "versioned_changelog",
        changelog_ok,
        f"CHANGELOG contains release {version}."
        if changelog_ok
        else f"CHANGELOG is missing a dated {version} section.",
    )

    readme = _read(root / "README.md")
    readme_requirements = (
        ("editable install", ("pip install --no-deps -e .",)),
        ("wheel build", ("pip wheel",)),
        ("source distribution build", ("setup.py sdist",)),
        ("install command", ("qacraft install", "scripts/qacraft.py install")),
        (
            "verify-install command",
            ("qacraft verify-install", "scripts/qacraft.py verify-install"),
        ),
        ("update command", ("qacraft update", "scripts/qacraft.py update")),
        ("uninstall command", ("qacraft uninstall", "scripts/qacraft.py uninstall")),
        ("evaluate command", ("qacraft evaluate", "scripts/qacraft.py evaluate")),
        (
            "release-check command",
            ("qacraft release-check", "scripts/qacraft.py release-check"),
        ),
        ("fixture catalog", ("evaluations/fixtures.json",)),
        ("demo command", ("scripts/demo.py",)),
        ("installation guide", ("docs/INSTALLATION.md",)),
        ("compatibility guide", ("docs/COMPATIBILITY.md",)),
        ("production-readiness guide", ("docs/PRODUCTION_READINESS.md",)),
    )
    missing_readme = [
        label
        for label, alternatives in readme_requirements
        if not any(token in readme for token in alternatives)
    ]
    _check(
        checks,
        "readme_quickstart",
        not missing_readme,
        "README documents source and artifact setup, lifecycle, evaluation fixtures, demo, and release checks."
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
        "Rubrics cover exactly the ten priority skills."
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

        allowed = rubric.get("allowed_decisions", [])
        unknown_decisions = sorted(set(allowed) - set(contract["decisions"]))
        if unknown_decisions:
            contract_errors.append(
                f"{skill}: decisions not present in SKILL.md: {unknown_decisions}"
            )

        unknown_success = sorted(
            set(rubric.get("success_decisions", [])) - set(allowed)
        )
        if unknown_success:
            contract_errors.append(
                f"{skill}: success decisions are not allowed: {unknown_success}"
            )

    _check(
        checks,
        "rubric_skill_binding",
        not contract_errors,
        "Every rubric is bound to its canonical skill gates, decisions, and outputs."
        if not contract_errors
        else "; ".join(contract_errors),
    )

    fixture_errors = _validate_published_fixtures(root, rubric_path, rubrics)
    _check(
        checks,
        "published_fixtures",
        not fixture_errors,
        "Published passing and targeted failure fixtures match their declared evaluation results."
        if not fixture_errors
        else "; ".join(fixture_errors),
    )

    phase_two = _read(root / "docs" / "PHASE_2.md")
    phase_complete = "Phase 2 is complete." in phase_two and "Next slice" not in phase_two
    _check(
        checks,
        "phase_two_complete",
        phase_complete,
        "Phase 2 is explicitly marked complete."
        if phase_complete
        else "docs/PHASE_2.md must explicitly mark Phase 2 complete.",
    )

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

    editable_cli_ok = (
        "[build-system]" in metadata
        and 'build-backend = "setuptools.build_meta"' in metadata
        and "[project.scripts]" in metadata
        and 'qacraft = "qacraft:main"' in metadata
        and 'packages = ["qacraft"]' in metadata
        and (root / "qacraft" / "__init__.py").is_file()
        and (root / "qacraft" / "__main__.py").is_file()
    )
    _check(
        checks,
        "editable_cli",
        editable_cli_ok,
        "Source and editable installations expose console and module entry points."
        if editable_cli_ok
        else "CLI metadata or entry-point files are incomplete.",
    )

    setup_text = _read(root / "setup.py")
    builder_text = _read(root / "qacraft_build.py")
    manifest_text = _read(root / "MANIFEST.in")
    manifest_tokens = (
        "recursive-include catalog",
        "recursive-include docs",
        "recursive-include evaluations",
        "recursive-include qacraft",
        "recursive-include schemas",
        "recursive-include scripts",
        "recursive-include shared",
        "recursive-include skills",
        "recursive-include tests",
    )
    builder_tokens = (
        "BUNDLE_PATHS",
        "BuildPyWithBundle",
        "qacraft/bundle",
        "Symbolic links are not allowed",
    )
    distribution_ok = (
        'distribution_mode = "bundled-artifacts"' in metadata
        and 'bundle_builder = "qacraft_build.py"' in metadata
        and 'source_manifest = "MANIFEST.in"' in metadata
        and "BuildPyWithBundle" in setup_text
        and all(token in builder_text for token in builder_tokens)
        and all(token in manifest_text for token in manifest_tokens)
    )
    _check(
        checks,
        "distribution_bundle",
        distribution_ok,
        "Wheel and source-distribution recipes include the reviewed runtime and canonical assets."
        if distribution_ok
        else "Distribution build recipe, manifest, or bundle metadata is incomplete.",
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
