from __future__ import annotations

import re
from pathlib import Path

import unittest
import run_test as rt


class TestGeneratedSpec(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.BASE_DIR = Path(__file__).resolve().parent.parent
        cls.component, cls.test_path, cls.spec_path = rt.read_config(cls.BASE_DIR)
        rt.run_generator(cls.BASE_DIR)

        cls.toc = cls.spec_path / f"{cls.component}_component_test.rst"
        cls.gen = cls.spec_path / f"{cls.component}_oAW_Generator_Tests.rst"
        cls.cmp = cls.spec_path / f"{cls.component}_oAW_Compiler_Tests.rst"
        cls.val = cls.spec_path / f"{cls.component}_oAW_Validator_Tests.rst"

    # Existence checks
    def test_files_exist(self) -> None:
        for p in [self.toc, self.gen, self.cmp, self.val]:
            rt.assert_exists(p)

    # TOC links present
    def test_toc_links_present(self) -> None:
        rt.assert_contains_substring(self.toc, f"{self.component}_oAW_Generator_Tests.rst")
        rt.assert_contains_substring(self.toc, f"{self.component}_oAW_Compiler_Tests.rst")
        rt.assert_contains_substring(self.toc, f"{self.component}_oAW_Validator_Tests.rst")

    # Comma-separated tags in headers
    def test_header_commas_present(self) -> None:
        rt.assert_regex(self.cmp, r"^\s*:tests: .*?, ")
        rt.assert_regex(self.gen, r"^\s*:tests: .*?, ")
        rt.assert_regex(self.val, r"^\s*:tests: .*?, ")

    # Header continuation indent in validator
    def test_validator_header_continuation_indent(self) -> None:
        rt.assert_regex(self.val, r"^\s{11}\S")
        rt.assert_regex(self.val, r"^\s{14}\S")

    # Placeholder tests for empty header .tsc
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

    # Deterministic ordering
    def test_deterministic_tag_order(self) -> None:
        rt.assert_contains_substring(
            self.cmp,
            ":tests: BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-6001, BSW_SEC_ModulesHere_Bogus-8001",
        )
        rt.assert_contains_substring(
            self.gen,
            ":tests: BSW_SEC_ModulesHere_Bogus-5048, BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-8001",
        )

    # No duplicate TOC links
    def test_toc_unique_links(self) -> None:
        toc_text = rt.read_text(self.toc)
        for fname in [
            f"{self.component}_oAW_Generator_Tests.rst",
            f"{self.component}_oAW_Compiler_Tests.rst",
            f"{self.component}_oAW_Validator_Tests.rst",
        ]:
            count = toc_text.count(fname)
            if count != 1:
                raise rt.TestError(f"Expected 1 occurrence of {fname}, found {count}")

    # Title underline length (120 '=' characters)
    def test_title_underline(self) -> None:
        for p in [self.gen, self.cmp, self.val]:
            lines = rt.read_text(p).splitlines()
            if len(lines) < 2:
                raise rt.TestError("File too short for title check")
            if set(lines[1]) != {"="} or len(lines[1]) != 120:
                raise rt.TestError("Expected second line to be 120 '='")

    # Section underline (dashes count equals section length)
    def test_section_underlines(self) -> None:
        def assert_section_underline(path: Path, section: str) -> None:
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

    # Group sw_test block id present
    def test_group_ids_present(self) -> None:
        rt.assert_regex(self.gen, rf"^\s*:id: TS_{self.component}_oAW_Generator_Tests$")
        rt.assert_regex(self.cmp, rf"^\s*:id: TS_{self.component}_oAW_Compiler_Tests$")
        rt.assert_regex(self.val, rf"^\s*:id: TS_{self.component}_oAW_Validator_Tests$")

    # IDs in per-file steps are sequential starting with 0001
    def test_id_sequences(self) -> None:
        def assert_id_sequence(path: Path, group: str) -> None:
            content = rt.read_text(path)
            ids = re.findall(rf":id: TSS_{self.component}_oAW_{group}_Tests_(\d{{4}})", content)
            if not ids:
                raise rt.TestError("No step IDs found")
            expected = [f"{i:04d}" for i in range(1, len(ids) + 1)]
            if ids != expected:
                raise rt.TestError(f"Expected {expected}, got {ids}")

        assert_id_sequence(self.gen, "Generator")
        assert_id_sequence(self.cmp, "Compiler")
        assert_id_sequence(self.val, "Validator")

    # Ensure all :tests: lines use ', '
    def test_tests_lines_use_comma_space(self) -> None:
        def assert_comma_space_only(path: Path) -> None:
            bad = []
            for ln in rt.read_text(path).splitlines():
                if ln.strip().startswith(":tests:") and re.search(r",\S", ln):
                    bad.append(ln)
            if bad:
                raise rt.TestError(f"Found bad lines: {bad[:2]}")

        assert_comma_space_only(self.gen)
        assert_comma_space_only(self.cmp)
        assert_comma_space_only(self.val)

    # Multiline field assertions for the multiline example test in Generator group
    def test_multiline_fields_present(self) -> None:
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

    # Indentation for continuation lines
    def test_continuation_indentation(self) -> None:
        rt.assert_regex(self.gen, r"^\s{19}It spans multiple lines to validate parsing behavior\.")
        rt.assert_regex(self.gen, r"^\s{13}Second line of input description\.")
        rt.assert_regex(self.gen, r"^\s{14}Second line of output description\.")

    # Exact title lines
    def test_title_lines(self) -> None:
        rt.assert_title_line(self.gen, "Generator Test Specification - oAW tests")
        rt.assert_title_line(self.cmp, "Compiler Test Specification - oAW tests")
        rt.assert_title_line(self.val, "Validator Test Specification - oAW tests")

    # Short descriptions per group
    def test_short_descriptions(self) -> None:
        rt.assert_shortdescription(self.gen, "Generate", self.component)
        rt.assert_shortdescription(self.cmp, "Compile", self.component)
        rt.assert_shortdescription(self.val, "Validate", self.component)

    # Group header aggregated tag sets: count, uniqueness, sorted
    def test_group_header_tag_sets(self) -> None:
        rt.assert_group_header_token_set(self.gen, 4)
        rt.assert_group_header_token_set(self.cmp, 3)
        rt.assert_group_header_token_set(self.val, 24)

    # Step block counts
    def test_step_block_counts(self) -> None:
        rt.assert_step_block_count(self.gen, 6)
        rt.assert_step_block_count(self.cmp, 4)
        rt.assert_step_block_count(self.val, 4)

    # Specific content checks for a few steps
    def test_specific_step_contents(self) -> None:
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

    # TOC order of generated files
    def test_toc_order(self) -> None:
        rt.assert_toc_order(
            self.toc,
            [
                f"{self.component}_oAW_Compiler_Tests.rst",
                f"{self.component}_oAW_Generator_Tests.rst",
                f"{self.component}_oAW_Validator_Tests.rst",
            ],
        )

    # Placeholder TODO count for EmptyHeader test
    def test_placeholder_todo_count(self) -> None:
        rt.assert_todo_count(self.val, 4)


if __name__ == "__main__":
    unittest.main()

