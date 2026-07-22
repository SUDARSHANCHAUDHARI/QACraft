#!/usr/bin/env python3
"""Read-only QACraft CLI foundation.

This module intentionally performs no installation or filesystem mutation.
It supports catalog discovery, repository health checks, and safe installation
planning so adapter behavior can be reviewed before write support is added.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "skills.json"
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
            path = ROOT / "skills" / slug / "SKILL.md"
            if not path.exists():
                errors.append(f"Missing skill definition: {path.relative_to(ROOT)}")

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
    print("Write operations: disabled in Phase 2.1")
    return 0


def command_plan_install(args: argparse.Namespace) -> int:
    skills = skill_map()

    if args.all and args.skills:
        print("Use either explicit skills or --all, not both.", file=sys.stderr)
        return 2

    selected = list(skills) if args.all else args.skills

    if not selected:
        print("Select one or more skills, or use --all.", file=sys.stderr)
        return 2

    unknown = sorted(set(selected) - set(skills))
    if unknown:
        print(f"Unknown skill(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    selected = sorted(set(selected))
    destination = Path(args.destination).expanduser()
    shared_sources = [f"shared/{name}" for name in REQUIRED_SHARED]
    plan = {
        "mode": "preview-only",
        "agent": args.agent,
        "destination": str(destination),
        "skills": selected,
        "shared_policies": list(REQUIRED_SHARED),
        "source_files": skill_source_files(selected) + shared_sources,
        "writes_performed": False,
        "notes": [
            "No files are copied or linked by Phase 2.1.",
            "Agent-specific destination rules are not yet enforced.",
            "A future installer must require overwrite review and rollback metadata.",
        ],
    }
    print(json.dumps(plan, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qacraft",
        description="Inspect QACraft and preview safe installation plans.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List available QA skills")
    list_parser.set_defaults(func=command_list)

    doctor_parser = sub.add_parser("doctor", help="Validate local QACraft structure")
    doctor_parser.set_defaults(func=command_doctor)

    plan_parser = sub.add_parser(
        "plan-install",
        help="Preview an installation plan without changing files",
    )
    plan_parser.add_argument("skills", nargs="*", help="Skill slugs without a leading slash")
    plan_parser.add_argument("--all", action="store_true", help="Select all skills")
    plan_parser.add_argument(
        "--agent",
        choices=SUPPORTED_AGENTS,
        default="generic",
        help="Target adapter contract",
    )
    plan_parser.add_argument(
        "--destination",
        required=True,
        help="Explicit destination to include in the preview",
    )
    plan_parser.set_defaults(func=command_plan_install)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())