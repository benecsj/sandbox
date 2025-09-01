"""Tests verifying generated files exist and TOC content/order is correct."""

from __future__ import annotations

import unittest

try:
    from tests._base import UnifiedTestCase
except ModuleNotFoundError:
    import os
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    from _base import UnifiedTestCase


class TestFilesAndTOC(UnifiedTestCase):
    """File presence and TOC linkage/order tests."""

    def test_files_exist(self) -> None:
        """All expected RST files are created by the generator."""
        for p in [self.toc, self.gen, self.cmp, self.val]:
            self.assert_exists(p)

    def test_toc_links_present(self) -> None:
        """TOC contains links to all generated group files exactly once."""
        self.assert_contains(self.toc, f"{self.component}_oAW_Generator_Tests.rst")
        self.assert_contains(self.toc, f"{self.component}_oAW_Compiler_Tests.rst")
        self.assert_contains(self.toc, f"{self.component}_oAW_Validator_Tests.rst")

    def test_toc_unique_links(self) -> None:
        """TOC references for each file are unique (no duplicates)."""
        toc_text = self.read_text(self.toc)
        for fname in [
            f"{self.component}_oAW_Generator_Tests.rst",
            f"{self.component}_oAW_Compiler_Tests.rst",
            f"{self.component}_oAW_Validator_Tests.rst",
        ]:
            count = toc_text.count(fname)
            if count != 1:
                raise AssertionError(f"Expected 1 occurrence of {fname}, found {count}")

    def test_toc_order(self) -> None:
        """TOC entries appear in deterministic order."""
        content = self.read_text(self.toc)
        files_in_order = [
            f"{self.component}_oAW_Compiler_Tests.rst",
            f"{self.component}_oAW_Generator_Tests.rst",
            f"{self.component}_oAW_Validator_Tests.rst",
        ]
        positions = [content.find(name) for name in files_in_order]
        if not (all(pos >= 0 for pos in positions) and positions == sorted(positions)):
            raise AssertionError(f"Positions not in order: {positions}")


if __name__ == "__main__":
    unittest.main()
