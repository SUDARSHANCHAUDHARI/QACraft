#!/usr/bin/env python3
"""Manifest-driven safe update support for QACraft."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from qacraft_installer import (
    MANIFEST_NAME,
    InstallError,
    load_manifest,
    reject_symlinked_target_path,
    resolve_destination,
    sha256_file,
    verify_installation,
)


def build_update_plan(
    root: Path,
    destination: Path,
    source_files: list[str],
    *,
    qacraft_version: str,
    agent: str,
    skills: list[str],
) -> dict:
    root = root.resolve(strict=True)
    destination, manifest = load_manifest(destination)
    manifest_path = destination / MANIFEST_NAME
    verification = verify_installation(destination)
    blocked = [item["path"] for item in verification["files"] if item["status"] != "ok"]
    if blocked:
        return {
            "mode": "preview-only",
            "destination": destination.as_posix(),
            "blocked": blocked,
            "operations": [],
            "writes_performed": False,
        }

    current = {item["path"]: item for item in manifest["files"]}
    desired: dict[str, dict] = {}

    for source_name in source_files:
        relative = Path(source_name)
        if relative.is_absolute() or ".." in relative.parts:
            raise InstallError(f"Unsafe source path: {source_name}")
        source = (root / relative).resolve(strict=True)
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise InstallError(f"Source escapes repository root: {source_name}") from exc
        desired[relative.as_posix()] = {
            "source": source,
            "sha256": sha256_file(source),
        }

    operations: list[dict] = []
    conflicts: list[str] = []

    for path, item in desired.items():
        relative = Path(path)
        reject_symlinked_target_path(destination, relative)
        target = destination / relative
        if path in current:
            if current[path].get("sha256") != item["sha256"]:
                operations.append(
                    {
                        "operation": "replace",
                        "path": path,
                        "source": item["source"].as_posix(),
                        "expected_sha256": current[path].get("sha256"),
                        "sha256": item["sha256"],
                    }
                )
        else:
            if target.exists() or target.is_symlink():
                conflicts.append(path)
            else:
                operations.append(
                    {
                        "operation": "create",
                        "path": path,
                        "source": item["source"].as_posix(),
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
        "updated_from_version": manifest.get("qacraft_version"),
        "destination": destination.as_posix(),
        "skills": sorted(set(skills)),
        "files": [
            {
                "path": path,
                "source": path,
                "sha256": desired[path]["sha256"],
                "operation": "create",
            }
            for path in sorted(desired)
        ],
    }

    return {
        "mode": "preview-only",
        "destination": destination.as_posix(),
        "manifest": manifest_path.as_posix(),
        "manifest_sha256": sha256_file(manifest_path),
        "operations": operations,
        "conflicts": conflicts,
        "blocked": [],
        "new_manifest": new_manifest,
        "writes_performed": False,
    }


def apply_update_plan(plan: dict) -> dict:
    if plan.get("blocked"):
        raise InstallError("Update refused because installed files are missing or modified.")
    if plan.get("conflicts"):
        raise InstallError("Update refused because unowned destination files already exist.")

    destination = resolve_destination(Path(plan["destination"]))
    manifest_path = destination / MANIFEST_NAME
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise InstallError("Manifest changed after preview.")
    if sha256_file(manifest_path) != plan.get("manifest_sha256"):
        raise InstallError("Manifest changed after preview.")

    current_manifest_bytes = manifest_path.read_bytes()
    backups: dict[Path, bytes] = {}
    created: list[Path] = []

    try:
        for item in plan["operations"]:
            relative = Path(item["path"])
            reject_symlinked_target_path(destination, relative)
            target = destination / relative
            operation = item["operation"]

            if operation in {"replace", "delete"}:
                if not target.is_file() or target.is_symlink():
                    raise InstallError(f"Managed file changed after preview: {target}")
                if sha256_file(target) != item.get("expected_sha256"):
                    raise InstallError(f"Managed file changed after preview: {target}")
                backups[target] = target.read_bytes()

            if operation == "create":
                if target.exists() or target.is_symlink():
                    raise InstallError(f"Destination changed after preview: {target}")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(Path(item["source"]), target)
                created.append(target)
                if sha256_file(target) != item["sha256"]:
                    raise InstallError(f"Checksum verification failed: {target}")
            elif operation == "replace":
                shutil.copyfile(Path(item["source"]), target)
                if sha256_file(target) != item["sha256"]:
                    raise InstallError(f"Checksum verification failed: {target}")
            elif operation == "delete":
                target.unlink()
            else:
                raise InstallError(f"Unknown update operation: {operation}")

        manifest_path.write_text(json.dumps(plan["new_manifest"], indent=2) + "\n", encoding="utf-8")
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        for path, content in backups.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        manifest_path.write_bytes(current_manifest_bytes)
        raise

    result = dict(plan)
    result.update({"mode": "applied", "writes_performed": True})
    return result
