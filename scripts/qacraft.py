#!/usr/bin/env python3
"""QACraft command-line interface."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from qacraft_installer import InstallError, apply_install_plan, build_install_plan
from qacraft_uninstaller import apply_uninstall_plan, build_uninstall_plan

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "skills.json"
PYPROJECT = ROOT / "pyproject.toml"
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
SUPPORTED_AGENTS = ("generic", "claude-code", "codex")


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


def source_files_for(selected: list[str]) -> list[str]:
    return skill_source_files(selected) + [f"shared/{name}" for name in REQUIRED_SHARED]


def command_list(_: argparse.Namespace) -> int:
    for skill in load_catalog()["skills"]:
        print(f"{skill['command']:<28} {skill['title']}")
    return 0


def command_doctor(_: argparse.Namespace) -> int:
    errors: list[str] = []
    if not CATALOG.exists():
        errors.append(f"Missing catalog: {CATALOG}")
    else:
        try:
            skills = load_catalog()["skills"]
        except (OSError, KeyError, json.JSONDecodeError) as exc:
            errors.append(f"Catalog is unreadable: {exc}")
            skills = []
        for skill in skills:
            slug = skill.get("slug", "")
            for source in skill_source_files([slug]):
                path = ROOT / source
                if not path.exists():
                    errors.append(f"Missing skill file: {path.relative_to(ROOT)}")
    for name in REQUIRED_SHARED:
        path = ROOT / "shared" / name
        if not path.exists():
            errors.append(f"Missing shared policy: {path.relative_to(ROOT)}")
    if errors:
        print("QACraft doctor found problems:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("QACraft doctor passed.")
    print(f"Repository: {ROOT}")
    print(f"Skills: {len(load_catalog()['skills'])}")
    print("Generic install and uninstall: available with explicit --apply")
    print("Agent-specific installers: preview-only")
    return 0


def command_plan_install(args: argparse.Namespace) -> int:
    selected, status = select_skills(args)
    if selected is None:
        return status
    plan = {
        "mode": "preview-only",
        "agent": args.agent,
        "destination": str(Path(args.destination).expanduser()),
        "skills": selected,
        "shared_policies": list(REQUIRED_SHARED),
        "source_files": source_files_for(selected),
        "writes_performed": False,
        "notes": [
            "No files are copied or linked by plan-install.",
            "Agent-specific destination rules are not yet enforced.",
            "Use the generic install command with --apply for controlled writes.",
        ],
    }
    print(json.dumps(plan, indent=2))
    return 0


def command_install(args: argparse.Namespace) -> int:
    selected, status = select_skills(args)
    if selected is None:
        return status
    if args.agent != "generic":
        print(
            "Only the generic adapter supports installation. Claude Code and Codex remain preview-only.",
            file=sys.stderr,
        )
        return 2
    try:
        plan = build_install_plan(ROOT, Path(args.destination), source_files_for(selected))
        plan.update({"agent": args.agent, "skills": selected, "shared_policies": list(REQUIRED_SHARED)})
        if args.apply:
            plan = apply_install_plan(
                plan,
                qacraft_version=load_version(),
                agent=args.agent,
                skills=selected,
            )
    except (InstallError, OSError, RuntimeError) as exc:
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(plan, indent=2))
    return 0


def command_uninstall(args: argparse.Namespace) -> int:
    try:
        plan = build_uninstall_plan(Path(args.destination))
        if args.apply:
            plan = apply_uninstall_plan(plan)
    except (InstallError, OSError, RuntimeError) as exc:
        print(f"Uninstall failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(plan, indent=2))
    return 0


def add_selection_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("skills", nargs="*", help="Skill slugs without a leading slash")
    parser.add_argument("--all", action="store_true", help="Select all skills")
    parser.add_argument(
        "--agent",
        choices=SUPPORTED_AGENTS,
        default="generic",
        help="Target adapter contract",
    )
    parser.add_argument("--destination", required=True, help="Explicit destination path")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qacraft", description="Inspect and manage QACraft skills safely.")
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List available QA skills")
    list_parser.set_defaults(func=command_list)

    doctor_parser = sub.add_parser("doctor", help="Validate local QACraft structure")
    doctor_parser.set_defaults(func=command_doctor)

    plan_parser = sub.add_parser("plan-install", help="Preview an installation without changing files")
    add_selection_arguments(plan_parser)
    plan_parser.set_defaults(func=command_plan_install)

    install_parser = sub.add_parser("install", help="Preview or apply a safe generic installation")
    add_selection_arguments(install_parser)
    install_parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform the reviewed installation; without this flag no files are written",
    )
    install_parser.set_defaults(func=command_install)

    uninstall_parser = sub.add_parser("uninstall", help="Preview or apply a manifest-driven uninstall")
    uninstall_parser.add_argument("--destination", required=True, help="Installed QACraft destination")
    uninstall_parser.add_argument(
        "--apply",
        action="store_true",
        help="Delete only checksum-matching files recorded by the manifest",
    )
    uninstall_parser.set_defaults(func=command_uninstall)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
