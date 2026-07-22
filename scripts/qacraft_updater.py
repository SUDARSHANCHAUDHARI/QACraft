#!/usr/bin/env python3
"""Manifest-driven safe update support for QACraft."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from qacraft_installer import (
    MANIFEST_NAME,
    InstallError,
    load_manifest,
    manifest_path_for,
    normalise_file_specs,
    reject_symlinked_target_path,
    resolve_destination,
    safe_relative_path,
    sha256_bytes,
    sha256_file,
    verify_installation,
)
from qacraft_transforms import normalise_transform, render_source_bytes


def build_update_plan(
    root: Path,
    destination: Path,
    file_specs: list[str | dict[str, str]],
    *,
    qacraft_version: str,
    agent: str,
    skills: list[str],
    manifest_relative: str | Path = MANIFEST_NAME,
) -> dict:
    root = root.resolve(strict=True)
    destination, manifest = load_manifest(destination, manifest_relative)
    manifest_relative_path, manifest_path = manifest_path_for(
        destination, manifest_relative
    )

    installed_agent = manifest.get("agent")
    if installed_agent != agent:
        raise InstallError(
            f"Installed adapter is {installed_agent!r}, not requested adapter {agent!r}."
        )

    verification = verify_installation(destination, manifest_relative)
    blocked = [item["path"] for item in verification["files"] if item["status"] != "ok"]
    if blocked:
        return {
            "mode": "preview-only",
            "destination": destination.as_posix(),
            "agent": agent,
            "manifest": manifest_path.as_posix(),
            "manifest_relative": manifest_relative_path.as_posix(),
            "blocked": blocked,
            "operations": [],
            "writes_performed": False,
        }

    current = {str(item["path"]): item for item in manifest["files"]}
    desired: dict[str, dict] = {}

    for source_relative, target_relative, transform in normalise_file_specs(file_specs):
        source = (root / source_relative).resolve(strict=True)
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise InstallError(f"Source escapes repository root: {source_relative}") from exc
        rendered = render_source_bytes(source, transform)
        desired[target_relative.as_posix()] = {
            "source": source,
            "source_path": source_relative.as_posix(),
            "transform": transform,
            "source_sha256": sha256_file(source),
            "sha256": sha256_bytes(rendered),
        }

    operations: list[dict] = []
    conflicts: list[str] = []

    for path, item in desired.items():
        relative = safe_relative_path(path, label="target")
        reject_symlinked_target_path(destination, relative)
        target = destination / relative
        if path in current:
            if current[path].get("sha256") != item["sha256"]:
                operations.append(
                    {
                        "operation": "replace",
                        "path": path,
                        "source": item["source"].as_posix(),
                        "source_path": item["source_path"],
                        "transform": item["transform"],
                        "source_sha256": item["source_sha256"],
                        "expected_sha256": current[path].get("sha256"),
                        "sha256": item["sha256"],
                    }
                )
        elif target.exists() or target.is_symlink():
            conflicts.append(path)
        else:
            operations.append(
                {
                    "operation": "create",
                    "path": path,
                    "source": item["source"].as_posix(),
                    "source_path": item["source_path"],
                    "transform": item["transform"],
                    "source_sha256": item["source_sha256"],
                    "sha256": item["sha256"],
                }
            )

    for path in sorted(set(current) - set(desired)):
        operations.append(
            {
                "operation": "delete",
                "path": path,
                "expected_sha256": current[path].get("sha256"),
            }
        )

    new_manifest = {
        "schema_version": 1,
        "qacraft_version": qacraft_version,
        "agent": agent,
        "installed_at": manifest.get("installed_at"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_from_version": manifest.get("qacraft_version"),
        "destination": destination.as_posix(),
        "manifest_path": manifest_relative_path.as_posix(),
        "skills": sorted(set(skills)),
        "files": [
            {
                "path": path,
                "source": desired[path]["source_path"],
                "transform": desired[path]["transform"],
                "source_sha256": desired[path]["source_sha256"],
                "sha256": desired[path]["sha256"],
                "operation": "create",
            }
            for path in sorted(desired)
        ],
    }

    return {
        "mode": "preview-only",
        "destination": destination.as_posix(),
        "agent": agent,
        "manifest": manifest_path.as_posix(),
        "manifest_relative": manifest_relative_path.as_posix(),
        "manifest_sha256": sha256_file(manifest_path),
        "operations": operations,
        "conflicts": sorted(set(conflicts)),
        "blocked": [],
        "new_manifest": new_manifest,
        "writes_performed": False,
    }


def _write_exclusive(content: bytes, target: Path) -> None:
    with target.open("xb") as handle:
        handle.write(content)


def _remove_empty_managed_directories(paths: list[Path], destination: Path) -> None:
    directories: set[Path] = set()
    for path in paths:
        current = path.parent
        while current != destination:
            try:
                current.relative_to(destination)
            except ValueError:
                break
            directories.add(current)
            current = current.parent
    for directory in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        if directory.is_symlink():
            continue
        try:
            directory.rmdir()
        except OSError:
            pass


def apply_update_plan(plan: dict) -> dict:
    if plan.get("blocked"):
        raise InstallError("Update refused because installed files are missing or modified.")
    if plan.get("conflicts"):
        raise InstallError("Update refused because unowned destination files already exist.")

    destination = resolve_destination(Path(plan["destination"]))
    manifest_relative = safe_relative_path(
        plan.get("manifest_relative", MANIFEST_NAME), label="manifest"
    )
    _, manifest_path = manifest_path_for(destination, manifest_relative)
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise InstallError("Manifest changed after preview.")
    if sha256_file(manifest_path) != plan.get("manifest_sha256"):
        raise InstallError("Manifest changed after preview.")

    current_manifest_bytes = manifest_path.read_bytes()
    backups: dict[Path, bytes] = {}
    created: list[Path] = []
    deleted: list[Path] = []

    try:
        for item in plan["operations"]:
            relative = safe_relative_path(item["path"], label="target")
            reject_symlinked_target_path(destination, relative)
            target = destination / relative
            operation = item["operation"]

            if operation in {"replace", "delete"}:
                if target.is_symlink() or not target.is_file():
                    raise InstallError(f"Managed file changed after preview: {target}")
                if sha256_file(target) != item.get("expected_sha256"):
                    raise InstallError(f"Managed file changed after preview: {target}")
                backups[target] = target.read_bytes()

            if operation in {"create", "replace"}:
                source = Path(item["source"])
                if sha256_file(source) != item.get("source_sha256"):
                    raise InstallError(f"Source changed after preview: {source}")
                transform = normalise_transform(item.get("transform"))
                rendered = render_source_bytes(source, transform)
                if sha256_bytes(rendered) != item["sha256"]:
                    raise InstallError(f"Rendered source changed after preview: {source}")

            if operation == "create":
                if target.exists() or target.is_symlink():
                    raise InstallError(f"Destination changed after preview: {target}")
                target.parent.mkdir(parents=True, exist_ok=True)
                reject_symlinked_target_path(destination, relative)
                _write_exclusive(rendered, target)
                created.append(target)
                if sha256_file(target) != item["sha256"]:
                    raise InstallError(f"Checksum verification failed: {target}")
            elif operation == "replace":
                target.write_bytes(rendered)
                if sha256_file(target) != item["sha256"]:
                    raise InstallError(f"Checksum verification failed: {target}")
            elif operation == "delete":
                target.unlink()
                deleted.append(target)
            else:
                raise InstallError(f"Unknown update operation: {operation}")

        manifest_path.write_text(
            json.dumps(plan["new_manifest"], indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        for path, content in backups.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(current_manifest_bytes)
        _remove_empty_managed_directories(created, destination)
        raise

    _remove_empty_managed_directories(deleted, destination)
    result = dict(plan)
    result.update({"mode": "applied", "writes_performed": True})
    return result
