#!/usr/bin/env python3
"""Safe generic filesystem installer for QACraft.

The installer is intentionally conservative:
- preview is the default;
- writes require explicit ``--apply``;
- existing destination files are never overwritten;
- all installed files are recorded in a destination-local manifest;
- source and destination containment are validated before copying;
- symlinked destination paths are rejected.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

MANIFEST_NAME = ".qacraft-manifest.json"


class InstallError(RuntimeError):
    """Raised when an installation cannot be completed safely."""


@dataclass(frozen=True)
class PlannedFile:
    source: Path
    relative_path: Path
    destination: Path
    sha256: str

    def as_dict(self) -> dict[str, str]:
        return {
            "source": self.source.as_posix(),
            "relative_path": self.relative_path.as_posix(),
            "destination": self.destination.as_posix(),
            "sha256": self.sha256,
            "operation": "create",
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_destination(destination: Path) -> Path:
    expanded = destination.expanduser()
    parent = expanded.parent.resolve(strict=True)
    candidate = parent / expanded.name

    if candidate == candidate.parent:
        raise InstallError("Destination cannot be a filesystem root.")
    if candidate.is_symlink():
        raise InstallError("Destination cannot be a symbolic link.")
    if candidate.exists() and not candidate.is_dir():
        raise InstallError("Destination must be a directory or a new path.")

    return candidate.resolve(strict=True) if candidate.exists() else candidate


def reject_symlinked_target_path(destination: Path, relative: Path) -> None:
    current = destination
    if current.is_symlink():
        raise InstallError(f"Destination path contains a symbolic link: {current}")

    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise InstallError(f"Destination path contains a symbolic link: {current}")
        if current.exists() and not current.is_dir():
            raise InstallError(f"Destination parent is not a directory: {current}")


def build_install_plan(root: Path, destination: Path, source_files: list[str]) -> dict:
    root = root.resolve(strict=True)
    destination = resolve_destination(destination)
    planned: list[PlannedFile] = []
    conflicts: list[str] = []

    manifest_path = destination / MANIFEST_NAME
    if manifest_path.exists() or manifest_path.is_symlink():
        conflicts.append(manifest_path.as_posix())

    for source_name in source_files:
        relative = Path(source_name)
        if relative.is_absolute() or ".." in relative.parts:
            raise InstallError(f"Unsafe source path: {source_name}")

        source = (root / relative).resolve(strict=True)
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise InstallError(f"Source escapes repository root: {source_name}") from exc

        reject_symlinked_target_path(destination, relative)
        target = destination / relative
        try:
            target.relative_to(destination)
        except ValueError as exc:
            raise InstallError(f"Destination escapes install root: {target}") from exc

        if target.exists() or target.is_symlink():
            conflicts.append(target.as_posix())

        planned.append(
            PlannedFile(
                source=source,
                relative_path=relative,
                destination=target,
                sha256=sha256_file(source),
            )
        )

    return {
        "mode": "preview-only",
        "destination": destination.as_posix(),
        "manifest": manifest_path.as_posix(),
        "files": [item.as_dict() for item in planned],
        "conflicts": sorted(set(conflicts)),
        "writes_performed": False,
    }


def apply_install_plan(plan: dict, *, qacraft_version: str, agent: str, skills: list[str]) -> dict:
    if plan.get("conflicts"):
        joined = "\n- ".join(plan["conflicts"])
        raise InstallError(f"Installation refused because destination files already exist:\n- {joined}")

    destination = resolve_destination(Path(plan["destination"]))
    created_files: list[Path] = []

    try:
        destination.mkdir(parents=True, exist_ok=True)
        for item in plan["files"]:
            source = Path(item["source"])
            relative = Path(item["relative_path"])
            reject_symlinked_target_path(destination, relative)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                raise InstallError(f"Destination changed after preview: {target}")
            shutil.copyfile(source, target)
            if sha256_file(target) != item["sha256"]:
                raise InstallError(f"Checksum verification failed: {target}")
            created_files.append(target)

        manifest = {
            "schema_version": 1,
            "qacraft_version": qacraft_version,
            "agent": agent,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "destination": destination.as_posix(),
            "skills": sorted(set(skills)),
            "files": [
                {
                    "path": Path(item["destination"]).relative_to(destination).as_posix(),
                    "source": Path(item["relative_path"]).as_posix(),
                    "sha256": item["sha256"],
                    "operation": "create",
                }
                for item in plan["files"]
            ],
        }
        manifest_path = destination / MANIFEST_NAME
        if manifest_path.exists() or manifest_path.is_symlink():
            raise InstallError(f"Destination changed after preview: {manifest_path}")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        created_files.append(manifest_path)
    except Exception:
        for path in reversed(created_files):
            path.unlink(missing_ok=True)
        _remove_empty_directories(destination)
        raise

    result = dict(plan)
    result["mode"] = "applied"
    result["writes_performed"] = True
    result["manifest"] = (destination / MANIFEST_NAME).as_posix()
    return result


def _remove_empty_directories(destination: Path) -> None:
    if not destination.exists() or destination.is_symlink():
        return
    directories = sorted(
        (path for path in destination.rglob("*") if path.is_dir() and not path.is_symlink()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        try:
            directory.rmdir()
        except OSError:
            pass
    try:
        destination.rmdir()
    except OSError:
        pass
