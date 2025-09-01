#!/usr/bin/env python3
from __future__ import annotations
import sys
import unittest


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
