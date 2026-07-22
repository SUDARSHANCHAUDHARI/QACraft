#!/usr/bin/env python3
"""Verified filesystem layouts for QACraft agent adapters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AdapterLayout:
    agent: str
    skills_root: Path
    shared_root: Path
    manifest_path: Path
    documentation: str


ADAPTERS = {
    "generic": AdapterLayout(
        agent="generic",
        skills_root=Path("skills"),
        shared_root=Path("shared"),
        manifest_path=Path(".qacraft-manifest.json"),
        documentation="Platform-neutral QACraft layout",
    ),
    "codex": AdapterLayout(
        agent="codex",
        skills_root=Path(".agents/skills"),
        shared_root=Path(".agents/qacraft/shared"),
        manifest_path=Path(".agents/qacraft/manifest.json"),
        documentation="https://learn.chatgpt.com/docs/build-skills",
    ),
    "claude-code": AdapterLayout(
        agent="claude-code",
        skills_root=Path(".claude/skills"),
        shared_root=Path(".claude/qacraft/shared"),
        manifest_path=Path(".claude/qacraft/manifest.json"),
        documentation="https://code.claude.com/docs/en/slash-commands",
    ),
    "github-copilot": AdapterLayout(
        agent="github-copilot",
        skills_root=Path(".github/skills"),
        shared_root=Path(".github/qacraft/shared"),
        manifest_path=Path(".github/qacraft/manifest.json"),
        documentation=(
            "https://docs.github.com/en/copilot/how-tos/copilot-on-github/"
            "customize-copilot/customize-cloud-agent/add-skills"
        ),
    ),
    "gemini-cli": AdapterLayout(
        agent="gemini-cli",
        skills_root=Path(".gemini/skills"),
        shared_root=Path(".gemini/qacraft/shared"),
        manifest_path=Path(".gemini/qacraft/manifest.json"),
        documentation="https://geminicli.com/docs/cli/skills/",
    ),
    "opencode": AdapterLayout(
        agent="opencode",
        skills_root=Path(".opencode/skills"),
        shared_root=Path(".opencode/qacraft/shared"),
        manifest_path=Path(".opencode/qacraft/manifest.json"),
        documentation="https://opencode.ai/docs/skills",
    ),
}

SKILL_FILES = (
    "SKILL.md",
    "templates/report.yaml",
    "examples/request.md",
    "examples/expected-output.md",
)
AGENT_SKILL_TRANSFORM = "agent-skill-frontmatter"


def layout_for(agent: str) -> AdapterLayout:
    try:
        return ADAPTERS[agent]
    except KeyError as exc:
        raise ValueError(f"Unsupported agent adapter: {agent}") from exc


def build_file_specs(
    agent: str,
    skills: list[str],
    shared_policies: list[str] | tuple[str, ...],
) -> list[dict[str, str]]:
    """Map immutable QACraft source files into an adapter-specific target layout."""

    layout = layout_for(agent)
    specs: list[dict[str, str]] = []

    for slug in sorted(set(skills)):
        for relative_name in SKILL_FILES:
            spec = {
                "source": (Path("skills") / slug / relative_name).as_posix(),
                "target": (layout.skills_root / slug / relative_name).as_posix(),
            }
            if agent != "generic" and relative_name == "SKILL.md":
                spec["transform"] = AGENT_SKILL_TRANSFORM
            specs.append(spec)

    for name in shared_policies:
        specs.append(
            {
                "source": (Path("shared") / name).as_posix(),
                "target": (layout.shared_root / name).as_posix(),
            }
        )

    return specs
