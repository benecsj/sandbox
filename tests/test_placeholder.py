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


class TestPlaceholderAndTodos(UnifiedTestCase):
    """Validation of TODO placeholders when header sections are empty."""

    def test_placeholder_todo_lines(self) -> None:
        """Validator file includes TODO placeholders for all four fields."""
        self.assert_contains(
            self.val,
            ":tests: TODO:Update the Requirements field in the header of Bogus_Validate_EmptyHeader.tsc",
        )
        self.assert_contains(
            self.val,
            "Description: TODO:Update the Description field in the header of Bogus_Validate_EmptyHeader.tsc",
        )
        self.assert_contains(
            self.val,
            "Input: TODO:Update the Input field in the header of Bogus_Validate_EmptyHeader.tsc",
        )
        self.assert_contains(
            self.val,
            "Output: TODO:Update the Output field in the header of Bogus_Validate_EmptyHeader.tsc",
        )

    def test_placeholder_todo_count(self) -> None:
        """Number of emitted TODO markers matches expectations."""
        count = self.read_text(self.val).count("TODO:Update")
        if count != 4:
            raise AssertionError(f"Expected 4 TODO lines, found {count}")


if __name__ == "__main__":
    unittest.main()
