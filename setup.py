"""Setuptools compatibility entry point for QACraft distribution builds."""

from setuptools import setup

from qacraft_build import BuildPyWithBundle


setup(cmdclass={"build_py": BuildPyWithBundle})
