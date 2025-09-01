#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import List


class TestError(AssertionError):
    """Raised when a harness assertion fails."""


def read_config(base_dir: Path) -> tuple[str, Path, Path]:
    """Load component, test and spec paths from config/config.json under base_dir.

    Converts relative paths (in the JSON) into absolute paths using the
    directory of the config file as the base.
    """
    config_path = base_dir / "config" / "config.json"
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    component = raw["component"]
    cfg_dir = config_path.parent
    test_path = (
        Path(raw["test_path"])
        if Path(raw["test_path"]).is_absolute()
        else (cfg_dir / raw["test_path"]).resolve()
    )
    spec_path = (
        Path(raw["spec_path"])
        if Path(raw["spec_path"]).is_absolute()
        else (cfg_dir / raw["spec_path"]).resolve()
    )
    return component, test_path, spec_path


def read_text(path: Path) -> str:
    """Read a UTF-8 text file and return its contents."""
    return path.read_text(encoding="utf-8")


def assert_contains_substring(path: Path, substring: str) -> None:
    """Deprecated: use tests._base.UnifiedTestCase.assertContains instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def assert_regex(path: Path, pattern: str) -> None:
    """Deprecated: use tests._base.UnifiedTestCase.assertRegexFile instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def assert_not_regex(path: Path, pattern: str) -> None:
    """Deprecated: use tests._base.UnifiedTestCase.assertNotRegexFile instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def assert_exists(path: Path) -> None:
    """Deprecated: use tests._base.UnifiedTestCase.assertExists instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def run_generator(script_dir: Path) -> None:
    """Run the generator script located in ``script_dir`` and raise on failure."""
    script = script_dir / "oaw_to_rst.py"
    subprocess.run([sys.executable, str(script)], check=True)


def extract_group_header_tests(path: Path) -> List[str]:
    """Deprecated: use tests._base.UnifiedTestCase._extractGroupHeaderTests instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def assert_group_header_token_set(path: Path, expected_count: int) -> None:
    """Deprecated: use tests._base.UnifiedTestCase.assertGroupHeaderTokenSet instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def count_step_blocks(path: Path) -> int:
    """Deprecated: use tests._base.UnifiedTestCase._countStepBlocks instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def assert_step_block_count(path: Path, expected: int) -> None:
    """Deprecated: use tests._base.UnifiedTestCase.assertStepBlockCount instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def assert_title_line(path: Path, expected_title: str) -> None:
    """Deprecated: use tests._base.UnifiedTestCase.assertTitleLine instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def assert_shortdescription(path: Path, group_word: str, component: str) -> None:
    """Deprecated: use tests._base.UnifiedTestCase.assertShortDescription instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def assert_toc_order(toc_path: Path, files_in_order: List[str]) -> None:
    """Deprecated: use tests._base.UnifiedTestCase.assertTocOrder instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


def assert_todo_count(path: Path, expected: int) -> None:
    """Deprecated: use tests._base.UnifiedTestCase.assertTodoCount instead."""
    raise NotImplementedError("Use base test assertion methods (CamelCase) instead of run_test helpers")


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
