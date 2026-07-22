"""Setuptools compatibility entry point for QACraft distribution builds."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from setuptools import setup

BUILD_HELPER = Path(__file__).resolve().with_name("qacraft_build.py")
spec = importlib.util.spec_from_file_location("_qacraft_build_backend", BUILD_HELPER)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load QACraft build helper: {BUILD_HELPER}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

setup(cmdclass={"build_py": module.BuildPyWithBundle})
