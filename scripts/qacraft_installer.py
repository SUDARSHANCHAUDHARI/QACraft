#!/usr/bin/env python3
"""Safe filesystem installation, verification, and uninstall support for QACraft."""

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
    source_path: Path
    relative_path: Path
    destination: Path
    sha256: str

    def as_dict(self) -> dict[str, str]:
        return {
            "source": self.source.as_posix(),
            "source_path": self.source_path.as_posix(),
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


def safe_relative_path(value: str | Path, *, label: str) -> Path:
    path = Path(value)
    if not path.parts or path == Path(".") or path.is_absolute() or ".." in path.parts:
        raise InstallError(f"Unsafe {label} path: {value}")
    return path


def normalise_file_specs(
    file_specs: list[str | dict[str, str]],
) -> list[tuple[Path, Path]]:
    normalised: list[tuple[Path, Path]] = []
    targets: set[str] = set()

    for spec in file_specs:
        if isinstance(spec, str):
            source_value = spec
            target_value = spec
        elif isinstance(spec, dict):
            source_value = str(spec.get("source", ""))
            target_value = str(spec.get("target", ""))
        else:
            raise InstallError(f"Unsupported file specification: {spec!r}")

        source_path = safe_relative_path(source_value, label="source")
        target_path = safe_relative_path(target_value, label="target")
        target_key = target_path.as_posix()
        if target_key in targets:
            raise InstallError(f"Duplicate target path in installation plan: {target_key}")
        targets.add(target_key)
        normalised.append((source_path, target_path))

    return normalised


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


def manifest_path_for(destination: Path, manifest_relative: str | Path) -> tuple[Path, Path]:
    relative = safe_relative_path(manifest_relative, label="manifest")
    reject_symlinked_target_path(destination, relative)
    path = destination / relative
    try:
        path.relative_to(destination)
    except ValueError as exc:
        raise InstallError(f"Manifest escapes installation destination: {path}") from exc
    return relative, path


def build_install_plan(
    root: Path,
    destination: Path,
    file_specs: list[str | dict[str, str]],
    *,
    manifest_relative: str | Path = MANIFEST_NAME,
) -> dict:
    root = root.resolve(strict=True)
    destination = resolve_destination(destination)
    planned: list[PlannedFile] = []
    conflicts: list[str] = []
    manifest_relative_path, manifest_path = manifest_path_for(destination, manifest_relative)

    if manifest_path.exists() or manifest_path.is_symlink():
        conflicts.append(manifest_path.as_posix())

    for source_relative, target_relative in normalise_file_specs(file_specs):
        source = (root / source_relative).resolve(strict=True)
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise InstallError(f"Source escapes repository root: {source_relative}") from exc

        reject_symlinked_target_path(destination, target_relative)
        target = destination / target_relative
        try:
            target.relative_to(destination)
        except ValueError as exc:
            raise InstallError(f"Destination escapes install root: {target}") from exc

        if target.exists() or target.is_symlink():
            conflicts.append(target.as_posix())
        planned.append(
            PlannedFile(
                source=source,
                source_path=source_relative,
                relative_path=target_relative,
                destination=target,
                sha256=sha256_file(source),
            )
        )

    return {
        "mode": "preview-only",
        "destination": destination.as_posix(),
        "manifest": manifest_path.as_posix(),
        "manifest_relative": manifest_relative_path.as_posix(),
        "files": [item.as_dict() for item in planned],
        "conflicts": sorted(set(conflicts)),
        "writes_performed": False,
    }


def _copy_exclusive(source: Path, target: Path) -> None:
    with source.open("rb") as source_handle, target.open("xb") as target_handle:
        shutil.copyfileobj(source_handle, target_handle)


def _remove_empty_managed_directories(paths: list[Path], destination: Path) -> None:
    """Remove only empty ancestors of managed paths, never the project root."""

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


def apply_install_plan(
    plan: dict,
    *,
    qacraft_version: str,
    agent: str,
    skills: list[str],
) -> dict:
    if plan.get("conflicts"):
        raise InstallError("Installation refused because destination files already exist.")

    destination = resolve_destination(Path(plan["destination"]))
    manifest_relative, manifest_path = manifest_path_for(
        destination,
        plan.get("manifest_relative", MANIFEST_NAME),
    )
    created_files: list[Path] = []

    try:
        destination.mkdir(parents=True, exist_ok=True)
        for item in plan["files"]:
            source = Path(item["source"])
            relative = safe_relative_path(item["relative_path"], label="target")
            reject_symlinked_target_path(destination, relative)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            reject_symlinked_target_path(destination, relative)
            if target.exists() or target.is_symlink():
                raise InstallError(f"Destination changed after preview: {target}")
            _copy_exclusive(source, target)
            created_files.append(target)
            if sha256_file(target) != item["sha256"]:
                raise InstallError(f"Checksum verification failed: {target}")

        manifest = {
            "schema_version": 1,
            "qacraft_version": qacraft_version,
            "agent": agent,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "destination": destination.as_posix(),
            "manifest_path": manifest_relative.as_posix(),
            "skills": sorted(set(skills)),
            "files": [
                {
                    "path": safe_relative_path(
                        item["relative_path"], label="target"
                    ).as_posix(),
                    "source": safe_relative_path(
                        item.get("source_path", item["relative_path"]),
                        label="source",
                    ).as_posix(),
                    "sha256": item["sha256"],
                    "operation": "create",
                }
                for item in plan["files"]
            ],
        }

        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        reject_symlinked_target_path(destination, manifest_relative)
        if manifest_path.exists() or manifest_path.is_symlink():
            raise InstallError(f"Destination changed after preview: {manifest_path}")
        with manifest_path.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(manifest, indent=2) + "\n")
        created_files.append(manifest_path)
    except Exception:
        for path in reversed(created_files):
            path.unlink(missing_ok=True)
        _remove_empty_managed_directories(created_files + [manifest_path], destination)
        raise

    result = dict(plan)
    result.update({"mode": "applied", "writes_performed": True})
    return result


def load_manifest(
    destination: Path,
    manifest_relative: str | Path = MANIFEST_NAME,
) -> tuple[Path, dict]:
    destination = resolve_destination(destination)
    relative, manifest_path = manifest_path_for(destination, manifest_relative)
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise InstallError(f"QACraft manifest not found: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallError(f"QACraft manifest is unreadable: {exc}") from exc
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), list):
        raise InstallError("Unsupported or invalid QACraft manifest.")
    recorded_manifest = manifest.get("manifest_path")
    if recorded_manifest and recorded_manifest != relative.as_posix():
        raise InstallError("QACraft manifest path does not match the requested adapter.")
    return destination, manifest


def verify_installation(
    destination: Path,
    manifest_relative: str | Path = MANIFEST_NAME,
) -> dict:
    destination, manifest = load_manifest(destination, manifest_relative)
    files: list[dict] = []
    healthy = True

    for entry in manifest["files"]:
        relative = safe_relative_path(entry.get("path", ""), label="manifest file")
        reject_symlinked_target_path(destination, relative)
        target = destination / relative
        if target.is_symlink() or not target.exists():
            status = "missing"
            actual = None
        elif not target.is_file():
            status = "modified"
            actual = None
        else:
            actual = sha256_file(target)
            status = "ok" if actual == entry.get("sha256") else "modified"
        healthy = healthy and status == "ok"
        files.append(
            {
                "path": relative.as_posix(),
                "status": status,
                "expected_sha256": entry.get("sha256"),
                "actual_sha256": actual,
            }
        )

    return {
        "destination": destination.as_posix(),
        "agent": manifest.get("agent"),
        "healthy": healthy,
        "files": files,
    }


def build_uninstall_plan(
    destination: Path,
    manifest_relative: str | Path = MANIFEST_NAME,
) -> dict:
    destination, manifest = load_manifest(destination, manifest_relative)
    relative, manifest_path = manifest_path_for(destination, manifest_relative)
    verification = verify_installation(destination, manifest_relative)
    blocked = [item["path"] for item in verification["files"] if item["status"] != "ok"]
    checksums = {
        str(item.get("path", "")): str(item.get("sha256", ""))
        for item in manifest["files"]
    }
    return {
        "mode": "preview-only",
        "destination": destination.as_posix(),
        "agent": manifest.get("agent"),
        "manifest": manifest_path.as_posix(),
        "manifest_relative": relative.as_posix(),
        "manifest_sha256": sha256_file(manifest_path),
        "files": [item["path"] for item in verification["files"] if item["status"] == "ok"],
        "file_checksums": checksums,
        "blocked": blocked,
        "writes_performed": False,
    }


def apply_uninstall_plan(plan: dict) -> dict:
    if plan.get("blocked"):
        raise InstallError("Uninstall refused because installed files are missing or modified.")

    destination = resolve_destination(Path(plan["destination"]))
    manifest_relative = safe_relative_path(
        plan.get("manifest_relative", MANIFEST_NAME), label="manifest"
    )
    _, manifest_path = manifest_path_for(destination, manifest_relative)
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise InstallError("Manifest changed after uninstall preview.")
    if sha256_file(manifest_path) != plan.get("manifest_sha256"):
        raise InstallError("Manifest changed after uninstall preview.")

    current = build_uninstall_plan(destination, manifest_relative)
    if (
        current.get("blocked")
        or current.get("files") != plan.get("files")
        or current.get("file_checksums") != plan.get("file_checksums")
    ):
        raise InstallError("Installation changed after uninstall preview.")

    managed_paths: list[Path] = []
    for relative_name in current["files"]:
        relative = safe_relative_path(relative_name, label="manifest file")
        reject_symlinked_target_path(destination, relative)
        target = destination / relative
        if target.is_symlink() or not target.is_file():
            raise InstallError(f"Managed file changed after preview: {target}")
        if sha256_file(target) != current["file_checksums"].get(relative_name):
            raise InstallError(f"Managed file changed after preview: {target}")
        managed_paths.append(target)

    for target in managed_paths:
        target.unlink()
    manifest_path.unlink()
    _remove_empty_managed_directories(managed_paths + [manifest_path], destination)

    result = dict(current)
    result.update({"mode": "applied", "writes_performed": True})
    return result
