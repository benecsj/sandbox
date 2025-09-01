from __future__ import annotations

"""Tests verifying generated files exist and TOC content/order is correct."""

from pathlib import Path
import unittest

try:
    from tests._base import UnifiedTestCase
except ModuleNotFoundError:  # Fallback when imported as top-level module
    import os
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    from _base import UnifiedTestCase
import run_test as rt


class TestFilesAndTOC(UnifiedTestCase):
    """File presence and TOC linkage/order tests."""

    def test_files_exist(self) -> None:
        """All expected RST files are created by the generator."""
        for p in [self.toc, self.gen, self.cmp, self.val]:
            rt.assert_exists(p)

    def test_toc_links_present(self) -> None:
        """TOC contains links to all generated group files exactly once."""
        rt.assert_contains_substring(self.toc, f"{self.component}_oAW_Generator_Tests.rst")
        rt.assert_contains_substring(self.toc, f"{self.component}_oAW_Compiler_Tests.rst")
        rt.assert_contains_substring(self.toc, f"{self.component}_oAW_Validator_Tests.rst")

    def test_toc_unique_links(self) -> None:
        """TOC references for each file are unique (no duplicates)."""
        toc_text = rt.read_text(self.toc)
        for fname in [
            f"{self.component}_oAW_Generator_Tests.rst",
            f"{self.component}_oAW_Compiler_Tests.rst",
            f"{self.component}_oAW_Validator_Tests.rst",
        ]:
            count = toc_text.count(fname)
            if count != 1:
                raise rt.TestError(f"Expected 1 occurrence of {fname}, found {count}")

    def test_toc_order(self) -> None:
        """TOC entries appear in deterministic order."""
        rt.assert_toc_order(
            self.toc,
            [
                f"{self.component}_oAW_Compiler_Tests.rst",
                f"{self.component}_oAW_Generator_Tests.rst",
                f"{self.component}_oAW_Validator_Tests.rst",
            ],
        )


if __name__ == "__main__":
    unittest.main()

