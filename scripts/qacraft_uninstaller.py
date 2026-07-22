#!/usr/bin/env python3
"""Manifest-driven safe uninstall support for QACraft."""

from __future__ import annotations

import json
from pathlib import Path

from qacraft_installer import MANIFEST_NAME, InstallError, sha256_file


def build_uninstall_plan(destination: Path) -> dict:
    destination = destination.expanduser()
    if destination.is_symlink():
        raise InstallError("Destination cannot be a symbolic link.")
    destination = destination.resolve(strict=True)
    if not destination.is_dir():
        raise InstallError("Destination must be a directory.")

    manifest_path = destination / MANIFEST_NAME
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise InstallError(f"Missing valid QACraft manifest: {manifest_path}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallError(f"Unreadable QACraft manifest: {exc}") from exc

    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), list):
        raise InstallError("Unsupported or invalid QACraft manifest.")

    files: list[dict] = []
    conflicts: list[str] = []
    for item in manifest["files"]:
        relative = Path(str(item.get("path", "")))
        expected = str(item.get("sha256", ""))
        if not relative.parts or relative.is_absolute() or ".." in relative.parts:
            raise InstallError(f"Unsafe manifest path: {relative}")

        target = destination / relative
        if target.is_symlink():
            conflicts.append(f"{relative.as_posix()}: symbolic link")
            status = "conflict"
        elif not target.exists():
            conflicts.append(f"{relative.as_posix()}: missing")
            status = "conflict"
        elif not target.is_file():
            conflicts.append(f"{relative.as_posix()}: not a file")
            status = "conflict"
        elif not expected or sha256_file(target) != expected:
            conflicts.append(f"{relative.as_posix()}: modified")
            status = "conflict"
        else:
            status = "delete"

        files.append({"path": relative.as_posix(), "status": status, "sha256": expected})

    return {
        "mode": "preview-only",
        "destination": destination.as_posix(),
        "manifest": manifest_path.as_posix(),
        "files": files,
        "conflicts": conflicts,
        "writes_performed": False,
    }


def apply_uninstall_plan(plan: dict) -> dict:
    if plan.get("conflicts"):
        joined = "\n- ".join(plan["conflicts"])
        raise InstallError(f"Uninstall refused because installed files changed:\n- {joined}")

    destination = Path(plan["destination"]).resolve(strict=True)
    manifest_path = destination / MANIFEST_NAME
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise InstallError("Manifest changed after preview.")

    # Rebuild the plan immediately before deletion to close preview/apply races.
    current = build_uninstall_plan(destination)
    if current.get("conflicts"):
        joined = "\n- ".join(current["conflicts"])
        raise InstallError(f"Uninstall refused because installed files changed:\n- {joined}")

    for item in current["files"]:
        (destination / item["path"]).unlink()

    manifest_path.unlink()
    _remove_empty_directories(destination)

    result = dict(current)
    result["mode"] = "applied"
    result["writes_performed"] = True
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
