from __future__ import annotations

import unittest

from tests._base import UnifiedTestCase
import run_test as rt


class TestHeadersAndFormatting(UnifiedTestCase):
    def test_header_commas_present(self) -> None:
        rt.assert_regex(self.cmp, r"^\s*:tests: .*?, ")
        rt.assert_regex(self.gen, r"^\s*:tests: .*?, ")
        rt.assert_regex(self.val, r"^\s*:tests: .*?, ")

    def test_validator_header_continuation_indent(self) -> None:
        rt.assert_regex(self.val, r"^\s{11}\S")
        rt.assert_regex(self.val, r"^\s{14}\S")

    def test_title_underline(self) -> None:
        for p in [self.gen, self.cmp, self.val]:
            lines = rt.read_text(p).splitlines()
            if len(lines) < 2:
                raise rt.TestError("File too short for title check")
            if set(lines[1]) != {"="} or len(lines[1]) != 120:
                raise rt.TestError("Expected second line to be 120 '='")

    def test_section_underlines(self) -> None:
        def assert_section_underline(path, section: str) -> None:
            lines = rt.read_text(path).splitlines()
            for i, ln in enumerate(lines):
                if ln.strip() == section:
                    if i + 1 < len(lines) and set(lines[i + 1]) == {"-"} and len(lines[i + 1]) == len(section):
                        return
                    raise rt.TestError("Dash underline length mismatch")
            raise rt.TestError("Section header not found")

        assert_section_underline(self.gen, f"{self.component}_oAW_Generator_Tests")
        assert_section_underline(self.cmp, f"{self.component}_oAW_Compiler_Tests")
        assert_section_underline(self.val, f"{self.component}_oAW_Validator_Tests")

    def test_title_lines(self) -> None:
        rt.assert_title_line(self.gen, "Generator Test Specification - oAW tests")
        rt.assert_title_line(self.cmp, "Compiler Test Specification - oAW tests")
        rt.assert_title_line(self.val, "Validator Test Specification - oAW tests")

    def test_short_descriptions(self) -> None:
        rt.assert_shortdescription(self.gen, "Generate", self.component)
        rt.assert_shortdescription(self.cmp, "Compile", self.component)
        rt.assert_shortdescription(self.val, "Validate", self.component)

    def test_tests_lines_use_comma_space(self) -> None:
        def assert_comma_space_only(path) -> None:
            bad = []
            for ln in rt.read_text(path).splitlines():
                if ln.strip().startswith(":tests:") and rt.re.search(r",\S", ln):
                    bad.append(ln)
            if bad:
                raise rt.TestError(f"Found bad lines: {bad[:2]}")

        assert_comma_space_only(self.gen)
        assert_comma_space_only(self.cmp)
        assert_comma_space_only(self.val)

    def test_continuation_indentation(self) -> None:
        rt.assert_regex(self.gen, r"^\s{19}It spans multiple lines to validate parsing behavior\.")
        rt.assert_regex(self.gen, r"^\s{13}Second line of input description\.")
        rt.assert_regex(self.gen, r"^\s{14}Second line of output description\.")


if __name__ == "__main__":
    unittest.main()

