"""QACraft command entry points for source and built distributions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Sequence

_RUNTIME_MODULE = "_qacraft_runtime"
_PACKAGE_ROOT = Path(__file__).resolve().parent
_REQUIRED_RUNTIME_PATHS = (
    Path("scripts/qacraft.py"),
    Path("catalog/skills.json"),
    Path("skills"),
    Path("shared"),
    Path("schemas"),
    Path("evaluations/rubrics.json"),
)


class DistributionAssetsMissing(RuntimeError):
    """Raised when neither checkout nor bundled runtime assets are complete."""


# Compatibility name retained for Phase 3.1 callers.
SourceCheckoutRequired = DistributionAssetsMissing


def _missing_assets(root: Path) -> list[str]:
    return [
        relative.as_posix()
        for relative in _REQUIRED_RUNTIME_PATHS
        if not (root / relative).exists()
    ]


def runtime_root() -> Path:
    """Return the complete checkout or bundled QACraft runtime root."""

    candidates = (
        ("source checkout", _PACKAGE_ROOT.parent),
        ("installed bundle", _PACKAGE_ROOT / "bundle"),
    )
    failures: list[str] = []
    for label, candidate in candidates:
        missing = _missing_assets(candidate)
        if not missing:
            return candidate
        failures.append(f"{label}: {', '.join(missing)}")

    raise DistributionAssetsMissing(
        "QACraft runtime assets are incomplete. Reinstall from a verified wheel or "
        "source distribution, or clone the repository and run "
        "`python -m pip install --no-deps -e .`. Missing assets — "
        + "; ".join(failures)
    )


def source_root() -> Path:
    """Compatibility alias returning the active QACraft runtime root."""

    return runtime_root()


def _load_runtime() -> ModuleType:
    existing = sys.modules.get(_RUNTIME_MODULE)
    if existing is not None:
        return existing

    root = runtime_root()
    scripts = root / "scripts"
    script = scripts / "qacraft.py"
    scripts_value = str(scripts)
    if scripts_value not in sys.path:
        sys.path.insert(0, scripts_value)

    spec = importlib.util.spec_from_file_location(_RUNTIME_MODULE, script)
    if spec is None or spec.loader is None:
        raise DistributionAssetsMissing(f"Unable to load QACraft runtime from {script}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[_RUNTIME_MODULE] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(_RUNTIME_MODULE, None)
        raise
    return module


def main(argv: Sequence[str] | None = None) -> int:
    """Run QACraft from a checkout, editable install, wheel, or source distribution."""

    try:
        runtime = _load_runtime()
    except DistributionAssetsMissing as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return int(runtime.main(list(argv) if argv is not None else None))


__all__ = [
    "DistributionAssetsMissing",
    "SourceCheckoutRequired",
    "main",
    "runtime_root",
    "source_root",
]
