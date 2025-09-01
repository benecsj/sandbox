#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


try:
    # Reuse functions from tests._base so a single source of truth exists
    from tests._base import read_config, read_text, run_generator  # type: ignore
except ModuleNotFoundError:
    # Allow running when tests not importable as a package
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tests"))
    from _base import read_config, read_text, run_generator  # type: ignore


def main() -> int:
    """Entry point: run unittest discovery under the ``tests`` package."""
    # Delegate to unittest discovery so simplified tests can run without CHECKS.

    # Ensure we can import as module name 'run_test' consistently
    sys.modules.setdefault("run_test", sys.modules[__name__])

    suite = unittest.defaultTestLoader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    # Ensure importing this script as "run_test" reuses the same module instance
    sys.modules.setdefault("run_test", sys.modules[__name__])
    sys.exit(main())
