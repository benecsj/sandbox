"""Tests asserting specific step content within generated group files."""

from __future__ import annotations

import unittest

try:
    from tests._base import UnifiedTestCase
except ModuleNotFoundError:
    import os
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    from _base import UnifiedTestCase


class TestSpecificStepContents(UnifiedTestCase):
    """Spot checks for step blocks' Description/Input/Output contents."""

    def test_multiline_fields_present(self) -> None:
        """Generator multiline example renders all continuation lines."""
        self.assert_contains(self.gen, ".. sw_test_step:: Bogus_Generate_MultilineExample")
        self.assert_contains(
            self.gen, "Description: This is a multi-line description for the generator test."
        )
        self.assert_contains(
            self.gen, "It spans multiple lines to validate parsing behavior."
        )
        self.assert_contains(self.gen, "Input: First line of input description.")
        self.assert_contains(self.gen, "Second line of input description.")
        self.assert_contains(self.gen, "Output: First line of output description.")
        self.assert_contains(self.gen, "Second line of output description.")

    def test_specific_step_contents(self) -> None:
        """Specific steps contain expected text snippets across groups."""
        self.assert_contains(self.cmp, ".. sw_test_step:: Bogus_Compile_KeyManagement")
        self.assert_contains(
            self.cmp,
            "Description: Ensures generated key management sources compile without errors.",
        )
        self.assert_contains(self.gen, ".. sw_test_step:: Bogus_Generate_Primitives")
        self.assert_contains(
            self.gen, "Input: Configurations for AES/HMAC primitive generation."
        )
        self.assert_contains(self.val, ".. sw_test_step:: Bogus_Validate_Config")
        self.assert_contains(self.val, "Output: Validation report without errors.")

        # Splitting behavior: subsequent numeric steps echo description but omit Input/Output
        self.assert_contains(self.gen, ".. sw_test_step:: Bogus_Generate_SplitTags")
        # Step 2 present with same Description
        self.assert_contains(self.gen, ".. sw_test_step:: 2")
        self.assert_contains(
            self.gen, "Description: Validate splitting of requirements into multiple numeric steps when exceeding threshold."
        )
        # Ensure Input is not repeated under step 2
        self.assert_not_regex_file(
            self.gen,
            r"\.. sw_test_step:: 2[\s\S]*?\n\s*Input:",
        )


if __name__ == "__main__":
    unittest.main()
