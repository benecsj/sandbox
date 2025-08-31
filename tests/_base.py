from __future__ import annotations

from pathlib import Path
import unittest
import run_test as rt
from lib.utils import ensure_jinja2_installed


class UnifiedTestCase(unittest.TestCase):
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

        cls.toc = cls.spec_path / f"{cls.component}_component_test.rst"
        cls.gen = cls.spec_path / f"{cls.component}_oAW_Generator_Tests.rst"
        cls.cmp = cls.spec_path / f"{cls.component}_oAW_Compiler_Tests.rst"
        cls.val = cls.spec_path / f"{cls.component}_oAW_Validator_Tests.rst"

    # Convenience wrappers mirroring harness helpers
    def assertExists(self, path: Path) -> None:  # noqa: N802 (keep unittest-style name)
        rt.assert_exists(path)

    def assertContains(self, path: Path, substring: str) -> None:  # noqa: N802
        rt.assert_contains_substring(path, substring)

    def assertRegexFile(self, path: Path, pattern: str) -> None:  # noqa: N802
        rt.assert_regex(path, pattern)

    def assertNotRegexFile(self, path: Path, pattern: str) -> None:  # noqa: N802
        rt.assert_not_regex(path, pattern)

