from __future__ import annotations

"""Tests asserting specific step content within generated group files."""

import unittest

try:
    from tests._base import UnifiedTestCase
except ModuleNotFoundError:
    import os
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    from _base import UnifiedTestCase
import run_test as rt


class TestSpecificStepContents(UnifiedTestCase):
    """Spot checks for step blocks' Description/Input/Output contents."""

    def test_multiline_fields_present(self) -> None:
        """Generator multiline example renders all continuation lines."""
        rt.assert_contains_substring(self.gen, ".. sw_test_step:: Bogus_Generate_MultilineExample")
        rt.assert_contains_substring(
            self.gen, "Description: This is a multi-line description for the generator test."
        )
        rt.assert_contains_substring(
            self.gen, "It spans multiple lines to validate parsing behavior."
        )
        rt.assert_contains_substring(self.gen, "Input: First line of input description.")
        rt.assert_contains_substring(self.gen, "Second line of input description.")
        rt.assert_contains_substring(self.gen, "Output: First line of output description.")
        rt.assert_contains_substring(self.gen, "Second line of output description.")

    def test_specific_step_contents(self) -> None:
        """Specific steps contain expected text snippets across groups."""
        rt.assert_contains_substring(self.cmp, ".. sw_test_step:: Bogus_Compile_KeyManagement")
        rt.assert_contains_substring(
            self.cmp, "Description: Ensures generated key management sources compile without errors."
        )
        rt.assert_contains_substring(self.gen, ".. sw_test_step:: Bogus_Generate_Primitives")
        rt.assert_contains_substring(
            self.gen, "Input: Configurations for AES/HMAC primitive generation."
        )
        rt.assert_contains_substring(self.val, ".. sw_test_step:: Bogus_Validate_Config")
        rt.assert_contains_substring(self.val, "Output: Validation report without errors.")


if __name__ == "__main__":
    unittest.main()

