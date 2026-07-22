"""QACraft source-checkout command entry point.

Phase 3.1 intentionally supports editable installation from a QACraft source
checkout. Wheel and source-distribution asset bundling are handled separately so
an incomplete package cannot silently omit skills, policies, schemas, or rubrics.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Sequence

_RUNTIME_MODULE = "_qacraft_source_runtime"


class SourceCheckoutRequired(RuntimeError):
    """Raised when the installed wrapper cannot locate the QACraft checkout."""


def source_root() -> Path:
    """Return the QACraft source root used by the editable installation."""

    root = Path(__file__).resolve().parents[1]
    required = (
        root / "scripts" / "qacraft.py",
        root / "catalog" / "skills.json",
        root / "skills",
        root / "shared",
        root / "evaluations" / "rubrics.json",
    )
    missing = [path.relative_to(root).as_posix() for path in required if not path.exists()]
    if missing:
        raise SourceCheckoutRequired(
            "QACraft's current console command requires an editable source checkout. "
            "Clone the repository and run `python -m pip install --no-deps -e .`. "
            f"Missing source assets: {', '.join(missing)}"
        )
    return root


def _load_runtime() -> ModuleType:
    existing = sys.modules.get(_RUNTIME_MODULE)
    if existing is not None:
        return existing

    root = source_root()
    scripts = root / "scripts"
    script = scripts / "qacraft.py"
    scripts_value = str(scripts)
    if scripts_value not in sys.path:
        sys.path.insert(0, scripts_value)

    spec = importlib.util.spec_from_file_location(_RUNTIME_MODULE, script)
    if spec is None or spec.loader is None:
        raise SourceCheckoutRequired(f"Unable to load QACraft runtime from {script}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[_RUNTIME_MODULE] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(_RUNTIME_MODULE, None)
        raise
    return module


def main(argv: Sequence[str] | None = None) -> int:
    """Run the existing QACraft CLI through an editable installation."""

    try:
        runtime = _load_runtime()
    except SourceCheckoutRequired as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return int(runtime.main(list(argv) if argv is not None else None))


__all__ = ["SourceCheckoutRequired", "main", "source_root"]
