"""Setuptools commands for building a self-contained QACraft distribution."""

from __future__ import annotations

import shutil
from pathlib import Path

from setuptools.command.build_py import build_py as _build_py

ROOT = Path(__file__).resolve().parent
BUNDLE_DISPLAY = "qacraft/bundle"
BUNDLE_RELATIVE = Path(BUNDLE_DISPLAY)

# One canonical source tree is kept in the repository. These reviewed paths are
# copied only into setuptools' temporary build directory.
BUNDLE_PATHS = (
    Path(".github/workflows/validate.yml"),
    Path("adapters"),
    Path("catalog"),
    Path("docs"),
    Path("evaluations"),
    Path("qacraft"),
    Path("schemas"),
    Path("scripts"),
    Path("shared"),
    Path("skills"),
    Path("AGENTS.md"),
    Path("CLAUDE.md"),
    Path("CHANGELOG.md"),
    Path("CONTRIBUTING.md"),
    Path("LICENSE"),
    Path("MANIFEST.in"),
    Path("README.md"),
    Path("SECURITY.md"),
    Path("index.html"),
    Path("pyproject.toml"),
    Path("qacraft_build.py"),
    Path("setup.py"),
)

EXCLUDED_NAMES = {
    ".DS_Store",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "venv",
}
EXCLUDED_SUFFIXES = (".egg-info", ".pyc", ".pyo")


def _excluded(path: Path) -> bool:
    return path.name in EXCLUDED_NAMES or path.name.endswith(EXCLUDED_SUFFIXES)


def _copy_reviewed_path(source: Path, destination: Path, outputs: list[str]) -> None:
    try:
        source.relative_to(ROOT)
    except ValueError as exc:
        raise RuntimeError(f"Bundle source escapes repository: {source}") from exc

    if source.is_symlink():
        raise RuntimeError(f"Symbolic links are not allowed in QACraft distributions: {source}")
    if _excluded(source):
        return
    if not source.exists():
        raise RuntimeError(f"Required QACraft distribution source is missing: {source}")

    if source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        outputs.append(str(destination))
        return

    if not source.is_dir():
        raise RuntimeError(f"Unsupported QACraft distribution source: {source}")

    destination.mkdir(parents=True, exist_ok=True)
    for child in sorted(source.iterdir(), key=lambda item: item.name):
        # Never ingest a previously generated bundle from the source package.
        if source == ROOT / "qacraft" and child.name == "bundle":
            continue
        _copy_reviewed_path(child, destination / child.name, outputs)


class BuildPyWithBundle(_build_py):
    """Copy canonical QACraft runtime assets into the wheel build directory."""

    def run(self) -> None:
        super().run()
        target = Path(self.build_lib) / BUNDLE_RELATIVE
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)

        outputs: list[str] = []
        for relative in BUNDLE_PATHS:
            _copy_reviewed_path(ROOT / relative, target / relative, outputs)
        self._qacraft_bundle_outputs = outputs

    def get_outputs(self, include_bytecode: int = 1) -> list[str]:
        outputs = list(super().get_outputs(include_bytecode))
        recorded = getattr(self, "_qacraft_bundle_outputs", None)
        if recorded is None:
            target = Path(self.build_lib) / BUNDLE_RELATIVE
            recorded = [str(path) for path in sorted(target.rglob("*")) if path.is_file()]
        outputs.extend(recorded)
        return outputs
