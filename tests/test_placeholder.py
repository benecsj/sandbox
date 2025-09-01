"""Tests covering TODO placeholder emission for empty headers."""

from __future__ import annotations

import unittest

try:
    from tests._base import UnifiedTestCase
except ModuleNotFoundError:
    import os
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    from _base import UnifiedTestCase
import run_test as rt


class TestPlaceholderAndTodos(UnifiedTestCase):
    """Validation of TODO placeholders when header sections are empty."""

    def test_placeholder_todo_lines(self) -> None:
        """Validator file includes TODO placeholders for all four fields."""
        rt.assert_contains_substring(
            self.val,
            ":tests: TODO:Update the Requirements field in the header of Bogus_Validate_EmptyHeader.tsc",
        )
        rt.assert_contains_substring(
            self.val,
            "Description: TODO:Update the Description field in the header of Bogus_Validate_EmptyHeader.tsc",
        )
        rt.assert_contains_substring(
            self.val,
            "Input: TODO:Update the Input field in the header of Bogus_Validate_EmptyHeader.tsc",
        )
        rt.assert_contains_substring(
            self.val,
            "Output: TODO:Update the Output field in the header of Bogus_Validate_EmptyHeader.tsc",
        )

    def test_placeholder_todo_count(self) -> None:
        """Number of emitted TODO markers matches expectations."""
        rt.assert_todo_count(self.val, 4)


if __name__ == "__main__":
    unittest.main()
