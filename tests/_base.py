"""Unit testing base class and utilities for the oAW to reStructuredText generator."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import unittest

try:
    import run_test as rt
except ModuleNotFoundError:
    # Ensure project root is on sys.path for direct test execution contexts
    ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(ROOT))
    import run_test as rt  # type: ignore


class UnifiedTestCase(unittest.TestCase):
    """Base class for all test cases, handling setup and common paths."""

    def setUp(self) -> None:
        # Mirror class attributes on the instance for environments relying on instance lookup
        cls = type(self)
        for name in ("BASE_DIR", "component", "test_path", "spec_path", "toc", "gen", "cmp", "val"):
            if hasattr(cls, name):
                setattr(self, name, getattr(cls, name))

    @classmethod
    def setUpClass(cls) -> None:
        cls.BASE_DIR = Path(__file__).resolve().parent.parent
        cls.component, cls.test_path, cls.spec_path = rt.read_config(cls.BASE_DIR)
        rt.run_generator(cls.BASE_DIR)
        # Set generated file paths for tests
        cls.toc = cls.spec_path / f"{cls.component}_component_test.rst"
        cls.gen = cls.spec_path / f"{cls.component}_oAW_Generator_Tests.rst"
        cls.cmp = cls.spec_path / f"{cls.component}_oAW_Compiler_Tests.rst"
        cls.val = cls.spec_path / f"{cls.component}_oAW_Validator_Tests.rst"

    # --- Convenience CLI helpers to match requested interface ---
    class CliResult:
        def __init__(self, exit_code: int, stdout: str, stderr: str) -> None:
            self.exit_code = exit_code
            self.stdout = stdout
            self.stderr = stderr

    def run_test(self, case_id: str) -> "UnifiedTestCase.CliResult":  # noqa: D401
        """Run the generator as a CLI invocation and return captured result.

        Note: case_id is accepted for compatibility but not used in this project.
        """
        script = self.BASE_DIR / "oaw_to_rst.py"
        proc = subprocess.run(
            [sys.executable, str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return UnifiedTestCase.CliResult(proc.returncode, proc.stdout, proc.stderr)

    def validate_execution_success(self, result: "UnifiedTestCase.CliResult") -> None:
        if result.exit_code != 0:
            raise AssertionError(f"CLI exited with {result.exit_code}: {result.stderr[:200]}")

    def validate_test_output(self, result: "UnifiedTestCase.CliResult") -> None:
        # Basic sanity: generated files exist
        for p in [self.toc, self.gen, self.cmp, self.val]:
            self.assert_exists(p)

    # Convenience helpers and assertions (snake_case naming)
    def read_text(self, path: Path) -> str:
        """Read a UTF-8 text file and return its contents."""
        return path.read_text(encoding="utf-8")

    def assert_exists(self, path: Path) -> None:
        """Assert that the given path exists."""
        if not path.exists():
            raise AssertionError(f"Expected file does not exist: {path}")

    def assert_contains(self, path: Path, substring: str) -> None:
        """Assert that ``substring`` exists within the file at ``path``."""
        content = self.read_text(path)
        if substring not in content:
            raise AssertionError(f"Expected substring not found in {path}: {substring}")

    def assert_regex_file(self, path: Path, pattern: str) -> None:
        """Assert that a regex ``pattern`` matches the file content at least once."""
        content = self.read_text(path)
        if re.search(pattern, content, re.MULTILINE) is None:
            raise AssertionError(f"Pattern not found in {path}: {pattern}")

    def assert_not_regex_file(self, path: Path, pattern: str) -> None:
        """Assert that a regex ``pattern`` does NOT match the file content."""
        content = self.read_text(path)
        if re.search(pattern, content, re.MULTILINE) is not None:
            raise AssertionError(f"Unexpected pattern present in {path}: {pattern}")
