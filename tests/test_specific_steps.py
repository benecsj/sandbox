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
        self.assertContains(self.gen, ".. sw_test_step:: Bogus_Generate_MultilineExample")
        self.assertContains(
            self.gen, "Description: This is a multi-line description for the generator test."
        )
        self.assertContains(
            self.gen, "It spans multiple lines to validate parsing behavior."
        )
        self.assertContains(self.gen, "Input: First line of input description.")
        self.assertContains(self.gen, "Second line of input description.")
        self.assertContains(self.gen, "Output: First line of output description.")
        self.assertContains(self.gen, "Second line of output description.")

    def test_specific_step_contents(self) -> None:
        """Specific steps contain expected text snippets across groups."""
        self.assertContains(self.cmp, ".. sw_test_step:: Bogus_Compile_KeyManagement")
        self.assertContains(
            self.cmp,
            "Description: Ensures generated key management sources compile without errors.",
        )
        self.assertContains(self.gen, ".. sw_test_step:: Bogus_Generate_Primitives")
        self.assertContains(
            self.gen, "Input: Configurations for AES/HMAC primitive generation."
        )
        self.assertContains(self.val, ".. sw_test_step:: Bogus_Validate_Config")
        self.assertContains(self.val, "Output: Validation report without errors.")


if __name__ == "__main__":
    unittest.main()
