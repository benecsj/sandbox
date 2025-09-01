"""Unit testing base class and utilities for the oAW to reStructuredText generator."""

from __future__ import annotations

from pathlib import Path
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
from lib.utils import ensure_jinja2_installed


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
        # Ensure Jinja2 is available before invoking the generator subprocess
        try:
            import jinja2  # noqa: F401
        except Exception:
            ensure_jinja2_installed()
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
            rt.assert_exists(p)

    # Convenience wrappers mirroring harness helpers
    def assertExists(self, path: Path) -> None:  # noqa: N802 (keep unittest-style name)
        """Wrapper for rt.assert_exists to match unittest style."""
        rt.assert_exists(path)

    def assertContains(self, path: Path, substring: str) -> None:  # noqa: N802
        """Wrapper for rt.assert_contains_substring to match unittest style."""
        rt.assert_contains_substring(path, substring)

    def assertRegexFile(self, path: Path, pattern: str) -> None:  # noqa: N802
        """Wrapper for rt.assert_regex to match unittest style."""
        rt.assert_regex(path, pattern)

    def assertNotRegexFile(self, path: Path, pattern: str) -> None:  # noqa: N802
        """Wrapper for rt.assert_not_regex to match unittest style."""
        rt.assert_not_regex(path, pattern)
