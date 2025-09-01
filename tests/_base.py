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

    def _extract_group_header_tests(self, path: Path) -> list[str]:
        """Extract tokens from the group header ``:tests:`` lines in a generated RST."""
        lines = self.read_text(path).splitlines()
        tokens: list[str] = []
        collecting = False
        for ln in lines:
            if not collecting and ln.strip().startswith(":tests:"):
                content = ln.split(":tests:", 1)[1]
                collecting = True
                segment = content.strip()
                if segment:
                    tokens.append(segment)
                continue
            if collecting:
                if ln.startswith("           ") and ln.strip():  # 11 spaces continuation
                    tokens.append(ln.strip())
                else:
                    break
        text = " ".join(tokens)
        parts = [p.strip() for p in text.replace(",", " ").split() if p.strip()]
        return parts

    def assert_group_header_token_set(self, path: Path, expected_count: int) -> None:
        """Assert group header tokens are unique, sorted, and match expected count."""
        tokens = self._extract_group_header_tests(path)
        unique = list(dict.fromkeys(tokens))
        is_sorted = tokens == sorted(tokens)
        if not ((len(tokens) == expected_count) and (len(unique) == len(tokens)) and is_sorted):
            raise AssertionError(
                "Count/unique/sort mismatch: "
                f"count={len(tokens)} expected={expected_count} "
                f"unique={len(unique)} sorted={is_sorted} tokens={tokens[:10]}..."
            )

    def _count_step_blocks(self, path: Path) -> int:
        """Count occurrences of ``.. sw_test_step::`` blocks in a file."""
        return sum(1 for ln in self.read_text(path).splitlines() if ln.strip().startswith(".. sw_test_step:: "))

    def assert_step_block_count(self, path: Path, expected: int) -> None:
        """Assert the number of step blocks in ``path`` equals ``expected``."""
        count = self._count_step_blocks(path)
        if count != expected:
            raise AssertionError(f"Expected {expected} step blocks, found {count}")

    def assert_title_line(self, path: Path, expected_title: str) -> None:
        """Assert the first line of the file equals ``expected_title``."""
        lines = self.read_text(path).splitlines()
        first = lines[0] if lines else ""
        if first != expected_title:
            raise AssertionError(f"Expected first line '{expected_title}', got '{first}'")

    def assert_short_description(self, path: Path, group_word: str, component: str) -> None:
        """Assert the group short description line contains the expected text."""
        expected = f":tst_shortdescription: Tests for successful {group_word} of {component}"
        self.assert_contains(path, expected)

    def assert_toc_order(self, toc_path: Path, files_in_order: list[str]) -> None:
        """Assert filenames appear in-order in the TOC file content."""
        content = self.read_text(toc_path)
        positions = [content.find(name) for name in files_in_order]
        if not (all(pos >= 0 for pos in positions) and positions == sorted(positions)):
            raise AssertionError(f"Positions not in order: {positions}")

    def assert_todo_count(self, path: Path, expected: int) -> None:
        """Assert the number of TODO markers in ``path`` equals ``expected``."""
        count = self.read_text(path).count("TODO:Update")
        if count != expected:
            raise AssertionError(f"Expected {expected} TODO lines, found {count}")

    # Backward-compat aliases (temporary)
    readText = read_text
    assertExists = assert_exists
    assertContains = assert_contains
    assertRegexFile = assert_regex_file
    assertNotRegexFile = assert_not_regex_file
    assertGroupHeaderTokenSet = assert_group_header_token_set
    assertStepBlockCount = assert_step_block_count
    assertTitleLine = assert_title_line
    assertShortDescription = assert_short_description
    assertTocOrder = assert_toc_order
    assertTodoCount = assert_todo_count
