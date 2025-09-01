"""Tests verifying header formatting, title/section underlines, and tag lines."""

from __future__ import annotations


import unittest

try:
    from tests._base import UnifiedTestCase
except ModuleNotFoundError:
    import os
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    from _base import UnifiedTestCase


class TestHeadersAndFormatting(UnifiedTestCase):
    """Formatting rules: commas, indentation, titles, sections, and tags."""

    def test_header_commas_present(self) -> None:
        """Group headers use comma+space separators in :tests: values."""
        self.assert_regex_file(self.cmp, r"^\s*:tests: .*?, ")
        self.assert_regex_file(self.gen, r"^\s*:tests: .*?, ")
        self.assert_regex_file(self.val, r"^\s*:tests: .*?, ")

    def test_validator_header_continuation_indent(self) -> None:
        """Validator file shows the 11 and 14 space continuation indents."""
        self.assert_regex_file(self.val, r"^\s{11}\S")
        self.assert_regex_file(self.val, r"^\s{14}\S")

    def test_title_underline(self) -> None:
        """Second line contains 120 '=' characters under the title."""
        for p in [self.gen, self.cmp, self.val]:
            lines = self.read_text(p).splitlines()
            if len(lines) < 2:
                raise AssertionError("File too short for title check")
            if set(lines[1]) != {"="} or len(lines[1]) != 120:
                raise AssertionError("Expected second line to be 120 '='")

    def test_section_underlines(self) -> None:
        """Section header dashes match the section title length."""

        def assert_section_underline(path, section: str) -> None:
            lines = self.read_text(path).splitlines()
            for i, ln in enumerate(lines):
                if ln.strip() == section:
                    if (
                        i + 1 < len(lines)
                        and set(lines[i + 1]) == {"-"}
                        and len(lines[i + 1]) == len(section)
                    ):
                        return
                    raise AssertionError("Dash underline length mismatch")
            raise AssertionError("Section header not found")

        assert_section_underline(self.gen, f"{self.component}_oAW_Generator_Tests")
        assert_section_underline(self.cmp, f"{self.component}_oAW_Compiler_Tests")
        assert_section_underline(self.val, f"{self.component}_oAW_Validator_Tests")

    def test_title_lines(self) -> None:
        """Title line text matches the expected strings per group."""
        self.assert_title_line(self.gen, "Generator Test Specification - oAW tests")
        self.assert_title_line(self.cmp, "Compiler Test Specification - oAW tests")
        self.assert_title_line(self.val, "Validator Test Specification - oAW tests")

    def test_short_descriptions(self) -> None:
        """Short description lines include group verb and component name."""
        self.assert_short_description(self.gen, "Generate", self.component)
        self.assert_short_description(self.cmp, "Compile", self.component)
        self.assert_short_description(self.val, "Validate", self.component)

    def test_tests_lines_use_comma_space(self) -> None:
        """All :tests: lines use comma+space; report any bad cases."""

        def assert_comma_space_only(path) -> None:
            bad = []
            for ln in self.read_text(path).splitlines():
                if ln.strip().startswith(":tests:") and __import__("re").search(r",\S", ln):
                    bad.append(ln)
            if bad:
                raise AssertionError(f"Found bad lines: {bad[:2]}")

        assert_comma_space_only(self.gen)
        assert_comma_space_only(self.cmp)
        assert_comma_space_only(self.val)

    def test_continuation_indentation(self) -> None:
        """Continuation indentation for multiline Description/Input/Output is correct."""
        self.assert_regex_file(self.gen, r"^\s{19}It spans multiple lines to validate parsing behavior\.")
        self.assert_regex_file(self.gen, r"^\s{13}Second line of input description\.")
        self.assert_regex_file(self.gen, r"^\s{14}Second line of output description\.")


if __name__ == "__main__":
    unittest.main()
