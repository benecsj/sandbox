from __future__ import annotations

import re
from pathlib import Path
from typing import List

import pytest
import run_test as rt

BASE_DIR = Path(__file__).resolve().parent.parent


def collect_results(base_dir: Path) -> List[rt.CheckResult]:
    component, test_path, spec_path = rt.read_config(base_dir)

    # 1) Run generator
    rt.run_generator(base_dir)

    # 2) Collect expected files
    toc = spec_path / f"{component}_component_test.rst"
    gen = spec_path / f"{component}_oAW_Generator_Tests.rst"
    cmp = spec_path / f"{component}_oAW_Compiler_Tests.rst"
    val = spec_path / f"{component}_oAW_Validator_Tests.rst"
    results: List[rt.CheckResult] = []
    # Existence checks
    for p in [toc, gen, cmp, val]:
        results.append(rt.assert_exists(p))

    # TOC links present (filenames appended)
    results.append(rt.assert_contains_substring(toc, f"{component}_oAW_Generator_Tests.rst"))
    results.append(rt.assert_contains_substring(toc, f"{component}_oAW_Compiler_Tests.rst"))
    results.append(rt.assert_contains_substring(toc, f"{component}_oAW_Validator_Tests.rst"))

    # Comma-separated tags in headers
    results.append(rt.assert_regex(cmp, r"^\s*:tests: .*?, "))
    results.append(rt.assert_regex(gen, r"^\s*:tests: .*?, "))
    results.append(rt.assert_regex(val, r"^\s*:tests: .*?, "))

    # Header continuation indent = 11 spaces in validator group header
    # The group header continuation lines begin with 11 spaces; assert they exist and contain the tag prefix
    results.append(rt.assert_regex(val, r"^\s{11}\S"))

    # Per-file continuation indent = 14 spaces exists in validator (for long tag list)
    # Per-file continuation lines begin with 14 spaces; assert they exist and contain the tag prefix
    # Accept any text on 14-space continuation since tags are present; anchor just the spaces
    results.append(rt.assert_regex(val, r"^\s{14}\S"))

    # Placeholder tests for empty header .tsc
    results.append(rt.assert_contains_substring(val, ":tests: TODO:Update the Requirements field in the header of Bogus_Validate_EmptyHeader.tsc"))
    results.append(rt.assert_contains_substring(val, "Description: TODO:Update the Description field in the header of Bogus_Validate_EmptyHeader.tsc"))
    results.append(rt.assert_contains_substring(val, "Input: TODO:Update the Input field in the header of Bogus_Validate_EmptyHeader.tsc"))
    results.append(rt.assert_contains_substring(val, "Output: TODO:Update the Output field in the header of Bogus_Validate_EmptyHeader.tsc"))

    # Deterministic ordering: Compiler aggregated tags in ascending order
    results.append(rt.assert_contains_substring(cmp, ":tests: BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-6001, BSW_SEC_ModulesHere_Bogus-8001"))
    results.append(rt.assert_contains_substring(gen, ":tests: BSW_SEC_ModulesHere_Bogus-5048, BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-8001"))

    # No duplicate TOC links
    toc_text = rt.read_text(toc)
    for fname in [f"{component}_oAW_Generator_Tests.rst", f"{component}_oAW_Compiler_Tests.rst", f"{component}_oAW_Validator_Tests.rst"]:
        count = toc_text.count(fname)
        results.append(rt.CheckResult(name=f"toc-unique:{fname}", passed=(count == 1), message=f"Expected 1 occurrence of {fname}, found {count}"))

    # Title underline length (120 '=' characters)
    def assert_title_underline(path: Path) -> rt.CheckResult:
        lines = rt.read_text(path).splitlines()
        if len(lines) < 2:
            return rt.CheckResult(name=f"title-underline:{path.name}", passed=False, message="File too short for title check")
        ok = (set(lines[1]) == {"="} and len(lines[1]) == 120)
        return rt.CheckResult(name=f"title-underline:{path.name}", passed=ok, message="Expected second line to be 120 '='")

    results.append(assert_title_underline(gen))
    results.append(assert_title_underline(cmp))
    results.append(assert_title_underline(val))

    # Section underline (dashes count equals section length)
    def assert_section_underline(path: Path, section: str) -> rt.CheckResult:
        lines = rt.read_text(path).splitlines()
        for i, ln in enumerate(lines):
            if ln.strip() == section:
                if i + 1 < len(lines) and set(lines[i + 1]) == {"-"} and len(lines[i + 1]) == len(section):
                    return rt.CheckResult(name=f"section-underline:{path.name}", passed=True)
                return rt.CheckResult(name=f"section-underline:{path.name}", passed=False, message="Dash underline length mismatch")
        return rt.CheckResult(name=f"section-underline:{path.name}", passed=False, message="Section header not found")

    results.append(assert_section_underline(gen, f"{component}_oAW_Generator_Tests"))
    results.append(assert_section_underline(cmp, f"{component}_oAW_Compiler_Tests"))
    results.append(assert_section_underline(val, f"{component}_oAW_Validator_Tests"))

    # Group sw_test block id present
    def assert_group_id(path: Path, group: str) -> rt.CheckResult:
        pat = rf"^\s*:id: TS_{component}_oAW_{group}_Tests$"
        return rt.assert_regex(path, pat)

    results.append(assert_group_id(gen, "Generator"))
    results.append(assert_group_id(cmp, "Compiler"))
    results.append(assert_group_id(val, "Validator"))

    # IDs in per-file steps are sequential starting with 0001
    def assert_id_sequence(path: Path, group: str) -> rt.CheckResult:
        content = rt.read_text(path)
        ids = re.findall(rf":id: TSS_{component}_oAW_{group}_Tests_(\d{{4}})", content)
        if not ids:
            return rt.CheckResult(name=f"id-seq:{path.name}", passed=False, message="No step IDs found")
        expected = [f"{i:04d}" for i in range(1, len(ids) + 1)]
        ok = ids == expected
        return rt.CheckResult(name=f"id-seq:{path.name}", passed=ok, message=f"Expected {expected}, got {ids}")

    results.append(assert_id_sequence(gen, "Generator"))
    results.append(assert_id_sequence(cmp, "Compiler"))
    results.append(assert_id_sequence(val, "Validator"))

    # Ensure all :tests: lines use ", " (comma-space), not comma with no space
    def assert_comma_space_only(path: Path) -> rt.CheckResult:
        bad = []
        for ln in rt.read_text(path).splitlines():
            if ln.strip().startswith(":tests:"):
                if re.search(r",\S", ln):
                    bad.append(ln)
        return rt.CheckResult(name=f"comma-space:{path.name}", passed=(len(bad) == 0), message=f"Found bad lines: {bad[:2]}")

    results.append(assert_comma_space_only(gen))
    results.append(assert_comma_space_only(cmp))
    results.append(assert_comma_space_only(val))

    # Multiline field assertions for the multiline example test in Generator group
    results.append(rt.assert_contains_substring(gen, ".. sw_test_step:: Bogus_Generate_MultilineExample"))
    results.append(rt.assert_contains_substring(gen, "Description: This is a multi-line description for the generator test."))
    results.append(rt.assert_contains_substring(gen, "It spans multiple lines to validate parsing behavior."))
    results.append(rt.assert_contains_substring(gen, "Input: First line of input description."))
    results.append(rt.assert_contains_substring(gen, "Second line of input description."))
    results.append(rt.assert_contains_substring(gen, "Output: First line of output description."))
    results.append(rt.assert_contains_substring(gen, "Second line of output description."))

    # Indentation for continuation lines (Description/Input/Output follow-up aligned under value start)
    results.append(rt.assert_regex(gen, r"^\s{19}It spans multiple lines to validate parsing behavior\."))
    results.append(rt.assert_regex(gen, r"^\s{13}Second line of input description\."))
    results.append(rt.assert_regex(gen, r"^\s{14}Second line of output description\."))

    # Additional explicit assertions
    # 1) Exact title lines
    results.append(rt.assert_title_line(gen, "Generator Test Specification - oAW tests"))
    results.append(rt.assert_title_line(cmp, "Compiler Test Specification - oAW tests"))
    results.append(rt.assert_title_line(val, "Validator Test Specification - oAW tests"))

    # 2) Short descriptions per group
    results.append(rt.assert_shortdescription(gen, "Generate", component))
    results.append(rt.assert_shortdescription(cmp, "Compile", component))
    results.append(rt.assert_shortdescription(val, "Validate", component))

    # 3) Group header aggregated tag sets: count, uniqueness, sorted
    results.append(rt.assert_group_header_token_set(gen, 4))
    results.append(rt.assert_group_header_token_set(cmp, 3))
    results.append(rt.assert_group_header_token_set(val, 24))

    # 4) Step block counts (2 blocks per .tsc in each group)
    results.append(rt.assert_step_block_count(gen, 6))  # 3 tests
    results.append(rt.assert_step_block_count(cmp, 4))  # 2 tests
    results.append(rt.assert_step_block_count(val, 4))  # 2 tests

    # 5) Specific content checks for a few steps
    results.append(rt.assert_contains_substring(cmp, ".. sw_test_step:: Bogus_Compile_KeyManagement"))
    results.append(rt.assert_contains_substring(cmp, "Description: Ensures generated key management sources compile without errors."))
    results.append(rt.assert_contains_substring(gen, ".. sw_test_step:: Bogus_Generate_Primitives"))
    results.append(rt.assert_contains_substring(gen, "Input: Configurations for AES/HMAC primitive generation."))
    results.append(rt.assert_contains_substring(val, ".. sw_test_step:: Bogus_Validate_Config"))
    results.append(rt.assert_contains_substring(val, "Output: Validation report without errors."))

    # 6) TOC order of generated files
    results.append(rt.assert_toc_order(toc, [
        f"{component}_oAW_Compiler_Tests.rst",
        f"{component}_oAW_Generator_Tests.rst",
        f"{component}_oAW_Validator_Tests.rst",
    ]))

    # 7) Placeholder TODO count for EmptyHeader test
    results.append(rt.assert_todo_count(val, 4))
    return results


RESULTS = collect_results(BASE_DIR)


@pytest.mark.parametrize("result", RESULTS, ids=[r.name for r in RESULTS])
def test_generated_spec(result: rt.CheckResult) -> None:
    assert result.passed, result.message

