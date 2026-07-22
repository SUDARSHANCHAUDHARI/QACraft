#!/usr/bin/env python3
"""Deterministic transforms for installed QACraft agent files."""

from __future__ import annotations

import json
from pathlib import Path

AGENT_SKILL_FRONTMATTER = "agent-skill-frontmatter"
SUPPORTED_TRANSFORMS = {AGENT_SKILL_FRONTMATTER}
STANDARD_FIELDS = (
    "name",
    "description",
    "license",
    "compatibility",
    "allowed-tools",
)


class TransformError(ValueError):
    """Raised when a source file cannot be transformed safely."""


def normalise_transform(value: object) -> str | None:
    if value in (None, ""):
        return None
    transform = str(value)
    if transform not in SUPPORTED_TRANSFORMS:
        raise TransformError(f"Unsupported file transform: {transform}")
    return transform


def render_source_bytes(source: Path, transform: str | None) -> bytes:
    if transform is None:
        return source.read_bytes()
    if transform == AGENT_SKILL_FRONTMATTER:
        text = source.read_text(encoding="utf-8")
        return normalise_agent_skill_frontmatter(text).encode("utf-8")
    raise TransformError(f"Unsupported file transform: {transform}")


def normalise_agent_skill_frontmatter(text: str) -> str:
    """Move QACraft custom fields under Agent Skills' metadata mapping."""

    if not text.startswith("---\n"):
        raise TransformError("SKILL.md must start with YAML frontmatter.")
    closing = text.find("\n---\n", 4)
    if closing == -1:
        raise TransformError("SKILL.md frontmatter is not closed.")

    frontmatter = text[4:closing]
    body = text[closing + 5 :]
    fields: dict[str, str] = {}

    for line in frontmatter.splitlines():
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            raise TransformError("Nested source frontmatter is not supported.")
        key, separator, value = line.partition(":")
        key = key.strip()
        if not separator or not key or key in fields:
            raise TransformError(f"Invalid source frontmatter line: {line}")
        fields[key] = value.strip()

    for required in ("name", "description"):
        if not fields.get(required):
            raise TransformError(f"SKILL.md frontmatter is missing {required}.")

    output = ["---"]
    for key in STANDARD_FIELDS:
        value = fields.pop(key, None)
        if value:
            output.append(f"{key}: {json.dumps(value)}")

    if fields:
        output.append("metadata:")
        for key in sorted(fields):
            metadata_key = f"qacraft-{key}"
            output.append(f"  {metadata_key}: {json.dumps(fields[key])}")

    output.append("---")
    return "\n".join(output) + "\n" + body
