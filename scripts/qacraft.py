#!/usr/bin/env python3
"""QACraft command-line interface."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from qacraft_installer import (
    InstallError,
    apply_install_plan,
    build_install_plan,
    verify_installation,
)
from qacraft_uninstaller import apply_uninstall_plan,