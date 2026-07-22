#!/usr/bin/env python3
"""QACraft command-line interface."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from qacraft_adapters import ADAPTERS, build_file_specs, layout_for
from qacraft_eval import EvaluationError, evaluate_file, load_rubrics
from qacraft_installer import (
    InstallError,
    apply_install_plan,
    apply_uninstall_plan,
    build_install_plan,
    build_uninstall_plan,
    verify_installation,
)
from qacraft_updater import apply_update_plan, build_update_plan

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "skills.json"
PYPROJECT = ROOT / "pyproject.toml"
EVALUATION_RUBRICS = ROOT / "evaluations" / "rubrics.json"
REQUIRED_SHARED = (
    "qa-standards.md",
    "security-boundaries.md",
    "approval-policy.md",
    "evidence-policy.md",
    "data-safety.md",
    "result-model.md",
    "publication-policy.md",
    "release-policy.md",
)
SUPPORTED_AGENTS = tuple(ADAPTERS)
EVALUATED_SKILLS = (
    "feature-qa",
    "ticket-review",
    "bug-report",
    "verify-fix",
    "release-qa",
)


def load_catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def load_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if not match:
        raise RuntimeError("Unable to read QACraft version from pyproject.toml")
    return match.group(1)


def skill_map() -> dict[str, dict]:
    return {skill["slug"]: skill for skill in load_catalog()["skills"]}


def skill_source_files(slugs: list[str]) -> list[str]:
    files: list[str] = []
    for slug in sorted(set(slugs)):
        files.extend(
            [
                f"skills/{slug}/SKILL.md",
                f"skills/{slug}/templates/report.yaml",
                f"skills/{slug}/examples/request.md",
                f"skills/{slug}/examples/expected-output.md",
            ]
        )
    return files


def select_skills(args: argparse.Namespace) -> tuple[list[str] | None, int]:
    skills = skill_map()
    if args.all and args.skills:
        print("Use either explicit skills or --all, not both.", file=sys.stderr)
        return None, 2
    selected = list(skills) if args.all else args.skills
    if not selected:
        print("Select one or more skills, or use --all.", file=sys.stderr)
        return None, 2
    unknown = sorted(set(selected) - set(skills))
    if unknown:
        print(f"Unknown skill(s): {', '.join(unknown)}", file=sys.stderr)
        return None, 2
    return sorted(set(selected)), 0


def file_specs_for(agent: str, selected: list[str]) -> list[dict[str, str]]:
    return build_file_specs(agent, selected, REQUIRED_SHARED)


def command_list(_: argparse.Namespace) -> int:
    for skill in load_catalog()["skills"]:
        print(f"{skill['command']:<28} {skill['title']}")
    return 0


def command_doctor(_: argparse.Namespace) -> int:
    errors: list[str] = []
    try:
        skills = load_catalog()["skills"]
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        errors.append(f"Catalog is unreadable: {exc}")
        skills = []

    for skill in skills:
        for source in skill_source_files([skill.get("slug", "")]):
            path = ROOT / source
            if not path.exists():
                errors.append(f"Missing skill file: {path.relative_to(ROOT)}")
    for name in REQUIRED_SHARED:
        path = ROOT / "shared" / name
        if not path.exists():
            errors.append(f"Missing shared policy: {path.relative_to(ROOT)}")

    try:
        rubrics = load_rubrics(EVALUATION_RUBRICS)
    except EvaluationError as exc:
        errors.append(f"Evaluation rubrics are unreadable: {exc}")
        rubrics = {}
    missing_rubrics = sorted(set(EVALUATED_SKILLS) - set(rubrics))
    extra_rubrics = sorted(set(rubrics) - set(EVALUATED_SKILLS))
    if missing_rubrics:
        errors.append(f"Missing evaluation rubrics: {missing_rubrics}")
    if extra_rubrics:
        errors.append(f"Unexpected evaluation rubrics: {extra_rubrics}")

    if errors:
        print("QACraft doctor found problems:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("QACraft doctor passed.")
    print(f"Repository: {ROOT}")
    print(f"Skills: {len(skills)}")
    print("Generic install, update, verification, and uninstall: available")
    print("Verified Codex and Claude Code adapters: available")
    print(f"Deterministic behavior rubrics: {len(rubrics)}")
    return 0


def build_adapter_install_plan(args: argparse.Namespace, selected: list[str]) -> dict:
    layout = layout_for(args.agent)
    specs = file_specs_for(args.agent, selected)
    plan = build_install_plan(
        ROOT,
        Path(args.destination),
        specs,
        manifest_relative=layout.manifest_path,
    )
    plan.update(
        {
            "agent": args.agent,
            "adapter_documentation": layout.documentation,
            "skills": selected,
            "shared_policies": list(REQUIRED_SHARED),
            "source_files": [item["source"] for item in specs],
            "target_files": [item["target"] for item in specs],
            "file_mappings": specs,
        }
    )
    return plan


def command_plan_install(args: argparse.Namespace) -> int:
    selected, status = select_skills(args)
    if selected is None:
        return status
    try:
        plan = build_adapter_install_plan(args, selected)
    except (InstallError, OSError, ValueError) as exc:
        print(f"Installation planning failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(plan, indent=2))
    return 0


def command_install(args: argparse.Namespace) -> int:
    selected, status = select_skills(args)
    if selected is None:
        return status
    try:
        plan = build_adapter_install_plan(args, selected)
        if args.apply:
            plan = apply_install_plan(
                plan,
                qacraft_version=load_version(),
                agent=args.agent,
                skills=selected,
            )
    except (InstallError, OSError, RuntimeError, ValueError) as exc:
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(plan, indent=2))
    return 0


def command_update(args: argparse.Namespace) -> int:
    selected, status = select_skills(args)
    if selected is None:
        return status
    try:
        layout = layout_for(args.agent)
        plan = build_update_plan(
            ROOT,
            Path(args.destination),
            file_specs_for(args.agent, selected),
            qacraft_version=load_version(),
            agent=args.agent,
            skills=selected,
            manifest_relative=layout.manifest_path,
        )
        if args.apply:
            plan = apply_update_plan(plan)
    except (InstallError, OSError, RuntimeError, ValueError) as exc:
        print(f"Update failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(plan, indent=2))
    return 0


def command_verify_install(args: argparse.Namespace) -> int:
    try:
        layout = layout_for(args.agent)
        result = verify_installation(
            Path(args.destination),
            manifest_relative=layout.manifest_path,
        )
    except (InstallError, OSError, ValueError) as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["healthy"] else 1


def command_uninstall(args: argparse.Namespace) -> int:
    try:
        layout = layout_for(args.agent)
        plan = build_uninstall_plan(
            Path(args.destination),
            manifest_relative=layout.manifest_path,
        )
        if args.apply:
            plan = apply_uninstall_plan(plan)
    except (InstallError, OSError, ValueError) as exc:
        print(f"Uninstall failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(plan, indent=2))
    return 0


def command_eval_list(args: argparse.Namespace) -> int:
    try:
        rubrics = load_rubrics(Path(args.rubrics))
    except EvaluationError as exc:
        print(f"Evaluation rubric loading failed: {exc}", file=sys.stderr)
        return 1
    for skill in sorted(rubrics):
        decisions = ", ".join(rubrics[skill].get("allowed_decisions", []))
        print(f"/{skill:<22} {decisions}")
    return 0


def command_evaluate(args: argparse.Namespace) -> int:
    try:
        report = evaluate_file(
            Path(args.input),
            Path(args.rubrics),
            skill=args.skill,
        )
    except EvaluationError as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


def add_agent_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--agent",
        choices=SUPPORTED_AGENTS,
        default="generic",
        help="Installation adapter layout",
    )


def add_selection_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("skills", nargs="*", help="Skill slugs without a leading slash")
    parser.add_argument("--all", action="store_true", help="Select all skills")
    add_agent_argument(parser)
    parser.add_argument("--destination", required=True, help="Explicit project or install root")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qacraft",
        description="Install QACraft skills and evaluate structured QA behavior safely.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    item = sub.add_parser("list", help="List available QA skills")
    item.set_defaults(func=command_list)
    item = sub.add_parser("doctor", help="Validate local QACraft structure")
    item.set_defaults(func=command_doctor)

    item = sub.add_parser("plan-install", help="Preview an adapter installation plan")
    add_selection_arguments(item)
    item.set_defaults(func=command_plan_install)

    item = sub.add_parser("install", help="Preview or apply an adapter installation")
    add_selection_arguments(item)
    item.add_argument("--apply", action="store_true", help="Perform the reviewed installation")
    item.set_defaults(func=command_install)

    item = sub.add_parser("update", help="Preview or apply a safe adapter update")
    item.add_argument("skills", nargs="*", help="Desired skill slugs after update")
    item.add_argument("--all", action="store_true", help="Select all skills")
    add_agent_argument(item)
    item.add_argument("--destination", required=True, help="Existing installation root")
    item.add_argument("--apply", action="store_true", help="Perform the reviewed update")
    item.set_defaults(func=command_update)

    item = sub.add_parser("verify-install", help="Verify an adapter installation")
    add_agent_argument(item)
    item.add_argument("--destination", required=True)
    item.set_defaults(func=command_verify_install)

    item = sub.add_parser("uninstall", help="Preview or apply safe manifest-based removal")
    add_agent_argument(item)
    item.add_argument("--destination", required=True)
    item.add_argument("--apply", action="store_true", help="Remove only unchanged manifest-owned files")
    item.set_defaults(func=command_uninstall)

    item = sub.add_parser("eval-list", help="List skills with deterministic behavior rubrics")
    item.add_argument(
        "--rubrics",
        default=str(EVALUATION_RUBRICS),
        help="Rubric catalog JSON path",
    )
    item.set_defaults(func=command_eval_list)

    item = sub.add_parser("evaluate", help="Evaluate a structured candidate report")
    item.add_argument("--input", required=True, help="Candidate report JSON path")
    item.add_argument("--skill", choices=EVALUATED_SKILLS, help="Override candidate skill")
    item.add_argument(
        "--rubrics",
        default=str(EVALUATION_RUBRICS),
        help="Rubric catalog JSON path",
    )
    item.set_defaults(func=command_evaluate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
