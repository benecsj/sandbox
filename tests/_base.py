"""Unit testing base class and utilities for the oAW to reStructuredText generator."""

from __future__ import annotations

from pathlib import Path
import json
import re
import subprocess
import sys
import unittest
from lib.utils import ensure_jinja2_installed

ROOT = Path(__file__).resolve().parent.parent


def read_config(base_dir: Path) -> tuple[str, Path, Path]:
    """Load component, test and spec paths from tests/config.json under base_dir.

    Converts relative paths (in the JSON) into absolute paths using the
    directory of the config file as the base.
    """
    config_path = base_dir / "tests" / "config.json"
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    component = raw["component"]
    cfg_dir = config_path.parent
    test_path = (
        Path(raw["test_path"]) if Path(raw["test_path"]).is_absolute() else (cfg_dir / raw["test_path"]).resolve()
    )
    spec_path = (
        Path(raw["spec_path"]) if Path(raw["spec_path"]).is_absolute() else (cfg_dir / raw["spec_path"]).resolve()
    )
    return component, test_path, spec_path


def read_text(path: Path) -> str:
    """Read a UTF-8 text file and return its contents."""
    return path.read_text(encoding="utf-8")


def run_generator(script_dir: Path) -> None:
    """Run the generator script located in ``script_dir`` and raise on failure."""
    script = script_dir / "oaw_to_rst.py"
    config_path = script_dir / "tests" / "config.json"
    ensure_jinja2_installed()
    subprocess.run([sys.executable, str(script), "--config", str(config_path)], check=True)


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
        cls.component, cls.test_path, cls.spec_path = read_config(cls.BASE_DIR)
        run_generator(cls.BASE_DIR)
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
        config_path = self.BASE_DIR / "tests" / "config.json"
        proc = subprocess.run(
            [sys.executable, str(script), "--config", str(config_path)],
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
        return read_text(path)

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
