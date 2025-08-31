from __future__ import annotations

import unittest

from tests._base import UnifiedTestCase
import run_test as rt


class TestPlaceholderAndTodos(UnifiedTestCase):
    def test_placeholder_todo_lines(self) -> None:
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
        rt.assert_todo_count(self.val, 4)


if __name__ == "__main__":
    unittest.main()

