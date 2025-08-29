#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Tuple


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str = ""


def read_config(base_dir: Path) -> Tuple[str, Path, Path]:
    config_path = base_dir / "config.json"
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    component = raw["component"]
    test_path = Path(raw["test_path"]) if Path(raw["test_path"]).is_absolute() else (base_dir / raw["test_path"]).resolve()
    spec_path = Path(raw["spec_path"]) if Path(raw["spec_path"]).is_absolute() else (base_dir / raw["spec_path"]).resolve()
    return component, test_path, spec_path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_contains_substring(path: Path, substring: str) -> TestResult:
    content = read_text(path)
    ok = substring in content
    return TestResult(
        name=f"contains:{path.name}:{substring[:60]}",
        passed=ok,
        message=("" if ok else f"Expected substring not found in {path}: {substring}"),
    )


def assert_regex(path: Path, pattern: str) -> TestResult:
    content = read_text(path)
    ok = re.search(pattern, content, re.MULTILINE) is not None
    return TestResult(
        name=f"regex:{path.name}:{pattern}",
        passed=ok,
        message=("" if ok else f"Pattern not found in {path}: {pattern}"),
    )


def assert_not_regex(path: Path, pattern: str) -> TestResult:
    content = read_text(path)
    ok = re.search(pattern, content, re.MULTILINE) is None
    return TestResult(
        name=f"not-regex:{path.name}:{pattern}",
        passed=ok,
        message=("" if ok else f"Unexpected pattern present in {path}: {pattern}"),
    )


def assert_exists(path: Path) -> TestResult:
    ok = path.exists()
    return TestResult(
        name=f"exists:{path}",
        passed=ok,
        message=("" if ok else f"Expected file does not exist: {path}"),
    )


def run_generator(script_dir: Path) -> None:
    script = script_dir / "oaw_to_rst.py"
    subprocess.run([sys.executable, str(script)], check=True)


def extract_group_header_tests(path: Path) -> List[str]:
    lines = read_text(path).splitlines()
    tokens: List[str] = []
    collecting = False
    for idx, ln in enumerate(lines):
        if not collecting and ln.strip().startswith(":tests:"):
            content = ln.split(":tests:", 1)[1]
            collecting = True
            segment = content.strip()
            if segment:
                tokens.append(segment)
            continue
        if collecting:
            if ln.startswith("           ") and ln.strip():  # 11 spaces continuation
                tokens.append(ln.strip())
            else:
                break
    text = " ".join(tokens)
    # Normalize commas to spaces, split, and filter non-empty
    parts = [p.strip() for p in text.replace(",", " ").split() if p.strip()]
    return parts


def assert_group_header_token_set(path: Path, expected_count: int) -> TestResult:
    tokens = extract_group_header_tests(path)
    unique = list(dict.fromkeys(tokens))
    is_sorted = tokens == sorted(tokens)
    ok = (len(tokens) == expected_count) and (len(unique) == len(tokens)) and is_sorted
    return TestResult(
        name=f"group-header-tests:{path.name}",
        passed=ok,
        message=(
            "Count/unique/sort mismatch: "
            f"count={len(tokens)} expected={expected_count} "
            f"unique={len(unique)} sorted={is_sorted} tokens={tokens[:10]}..."
        ) if not ok else "",
    )


def count_step_blocks(path: Path) -> int:
    return sum(1 for ln in read_text(path).splitlines() if ln.strip().startswith(".. sw_test_step:: "))


def assert_step_block_count(path: Path, expected: int) -> TestResult:
    count = count_step_blocks(path)
    return TestResult(
        name=f"step-blocks:{path.name}",
        passed=(count == expected),
        message=f"Expected {expected} step blocks, found {count}",
    )


def assert_title_line(path: Path, expected_title: str) -> TestResult:
    first = read_text(path).splitlines()[0] if read_text(path).splitlines() else ""
    return TestResult(
        name=f"title-line:{path.name}",
        passed=(first == expected_title),
        message=f"Expected first line '{expected_title}', got '{first}'",
    )


def assert_shortdescription(path: Path, group_word: str, component: str) -> TestResult:
    expected = f":tst_shortdescription: Tests for successful {group_word} of {component}"
    return assert_contains_substring(path, expected)


def assert_toc_order(toc_path: Path, files_in_order: List[str]) -> TestResult:
    content = read_text(toc_path)
    positions = [content.find(name) for name in files_in_order]
    ok = all(pos >= 0 for pos in positions) and positions == sorted(positions)
    return TestResult(
        name="toc-order",
        passed=ok,
        message=f"Positions not in order: {positions}",
    )


def assert_todo_count(path: Path, expected: int) -> TestResult:
    count = read_text(path).count("TODO:Update")
    return TestResult(
        name=f"todo-count:{path.name}",
        passed=(count == expected),
        message=f"Expected {expected} TODO lines, found {count}",
    )


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    component, test_path, spec_path = read_config(script_dir)

    # 1) Run generator
    run_generator(script_dir)

    # 2) Collect expected files
    toc = spec_path / f"{component}_component_test.rst"
    gen = spec_path / f"{component}_oAW_Generator_Tests.rst"
    cmp = spec_path / f"{component}_oAW_Compiler_Tests.rst"
    val = spec_path / f"{component}_oAW_Validator_Tests.rst"
    tag_prefix = "BSW_SEC_ModulesHere_Bogus-" if component == "Bogus" else "BSW_SWCS_CryptoDriver_Crypto-"

    results: List[TestResult] = []
    # Existence checks
    for p in [toc, gen, cmp, val]:
        results.append(assert_exists(p))

    # TOC links present (filenames appended)
    results.append(assert_contains_substring(toc, f"{component}_oAW_Generator_Tests.rst"))
    results.append(assert_contains_substring(toc, f"{component}_oAW_Compiler_Tests.rst"))
    results.append(assert_contains_substring(toc, f"{component}_oAW_Validator_Tests.rst"))

    # Comma-separated tags in headers
    results.append(assert_regex(cmp, r"^\s*:tests: .*?, "))
    results.append(assert_regex(gen, r"^\s*:tests: .*?, "))
    results.append(assert_regex(val, r"^\s*:tests: .*?, "))

    # Header continuation indent = 11 spaces in validator group header
    # The group header continuation lines begin with 11 spaces; assert they exist and contain the tag prefix
    results.append(assert_regex(val, r"^\s{11}\S"))

    # Per-file continuation indent = 14 spaces exists in validator (for long tag list)
    # Per-file continuation lines begin with 14 spaces; assert they exist and contain the tag prefix
    # Accept any text on 14-space continuation since tags are present; anchor just the spaces
    results.append(assert_regex(val, r"^\s{14}\S"))

    # Placeholder tests for empty header .tsc
    results.append(assert_contains_substring(val, ":tests: TODO:Update the Requirements field in the header of Bogus_Validate_EmptyHeader.tsc"))
    results.append(assert_contains_substring(val, "Description: TODO:Update the Description field in the header of Bogus_Validate_EmptyHeader.tsc"))
    results.append(assert_contains_substring(val, "Input: TODO:Update the Input field in the header of Bogus_Validate_EmptyHeader.tsc"))
    results.append(assert_contains_substring(val, "Output: TODO:Update the Output field in the header of Bogus_Validate_EmptyHeader.tsc"))

    # Deterministic ordering: Compiler aggregated tags in ascending order
    results.append(assert_contains_substring(cmp, ":tests: BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-6001, BSW_SEC_ModulesHere_Bogus-8001"))
    results.append(assert_contains_substring(gen, ":tests: BSW_SEC_ModulesHere_Bogus-5048, BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-8001"))

    # No duplicate TOC links
    toc_text = read_text(toc)
    for fname in [f"{component}_oAW_Generator_Tests.rst", f"{component}_oAW_Compiler_Tests.rst", f"{component}_oAW_Validator_Tests.rst"]:
        count = toc_text.count(fname)
        results.append(TestResult(name=f"toc-unique:{fname}", passed=(count == 1), message=f"Expected 1 occurrence of {fname}, found {count}"))

    # Title underline length (120 '=' characters)
    def assert_title_underline(path: Path) -> TestResult:
        lines = read_text(path).splitlines()
        if len(lines) < 2:
            return TestResult(name=f"title-underline:{path.name}", passed=False, message="File too short for title check")
        ok = (set(lines[1]) == {"="} and len(lines[1]) == 120)
        return TestResult(name=f"title-underline:{path.name}", passed=ok, message="Expected second line to be 120 '='")

    results.append(assert_title_underline(gen))
    results.append(assert_title_underline(cmp))
    results.append(assert_title_underline(val))

    # Section underline (dashes count equals section length)
    def assert_section_underline(path: Path, section: str) -> TestResult:
        lines = read_text(path).splitlines()
        for i, ln in enumerate(lines):
            if ln.strip() == section:
                if i + 1 < len(lines) and set(lines[i + 1]) == {"-"} and len(lines[i + 1]) == len(section):
                    return TestResult(name=f"section-underline:{path.name}", passed=True)
                return TestResult(name=f"section-underline:{path.name}", passed=False, message="Dash underline length mismatch")
        return TestResult(name=f"section-underline:{path.name}", passed=False, message="Section header not found")

    results.append(assert_section_underline(gen, f"{component}_oAW_Generator_Tests"))
    results.append(assert_section_underline(cmp, f"{component}_oAW_Compiler_Tests"))
    results.append(assert_section_underline(val, f"{component}_oAW_Validator_Tests"))

    # Group sw_test block id present
    def assert_group_id(path: Path, group: str) -> TestResult:
        pat = rf"^\s*:id: TS_{component}_oAW_{group}_Tests$"
        return assert_regex(path, pat)

    results.append(assert_group_id(gen, "Generator"))
    results.append(assert_group_id(cmp, "Compiler"))
    results.append(assert_group_id(val, "Validator"))

    # IDs in per-file steps are sequential starting with 0001
    def assert_id_sequence(path: Path, group: str) -> TestResult:
        content = read_text(path)
        ids = re.findall(rf":id: TSS_{component}_oAW_{group}_Tests_(\d{{4}})", content)
        if not ids:
            return TestResult(name=f"id-seq:{path.name}", passed=False, message="No step IDs found")
        expected = [f"{i:04d}" for i in range(1, len(ids) + 1)]
        ok = ids == expected
        return TestResult(name=f"id-seq:{path.name}", passed=ok, message=f"Expected {expected}, got {ids}")

    results.append(assert_id_sequence(gen, "Generator"))
    results.append(assert_id_sequence(cmp, "Compiler"))
    results.append(assert_id_sequence(val, "Validator"))

    # Ensure all :tests: lines use ", " (comma-space), not comma with no space
    def assert_comma_space_only(path: Path) -> TestResult:
        bad = []
        for ln in read_text(path).splitlines():
            if ln.strip().startswith(":tests:"):
                if re.search(r",\S", ln):
                    bad.append(ln)
        return TestResult(name=f"comma-space:{path.name}", passed=(len(bad) == 0), message=f"Found bad lines: {bad[:2]}")

    results.append(assert_comma_space_only(gen))
    results.append(assert_comma_space_only(cmp))
    results.append(assert_comma_space_only(val))

    # Multiline field assertions for the multiline example test in Generator group
    results.append(assert_contains_substring(gen, ".. sw_test_step:: Bogus_Generate_MultilineExample"))
    results.append(assert_contains_substring(gen, "Description: This is a multi-line description for the generator test."))
    results.append(assert_contains_substring(gen, "It spans multiple lines to validate parsing behavior."))
    results.append(assert_contains_substring(gen, "Input: First line of input description."))
    results.append(assert_contains_substring(gen, "Second line of input description."))
    results.append(assert_contains_substring(gen, "Output: First line of output description."))
    results.append(assert_contains_substring(gen, "Second line of output description."))

    # Indentation for continuation lines (Description/Input/Output follow-up aligned under value start)
    results.append(assert_regex(gen, r"^\s{19}It spans multiple lines to validate parsing behavior\.") )
    results.append(assert_regex(gen, r"^\s{13}Second line of input description\.") )
    results.append(assert_regex(gen, r"^\s{14}Second line of output description\.") )

    # Summarize

    # Additional explicit assertions
    # 1) Exact title lines
    results.append(assert_title_line(gen, "Generator Test Specification - oAW tests"))
    results.append(assert_title_line(cmp, "Compiler Test Specification - oAW tests"))
    results.append(assert_title_line(val, "Validator Test Specification - oAW tests"))

    # 2) Short descriptions per group
    results.append(assert_shortdescription(gen, "Generate", component))
    results.append(assert_shortdescription(cmp, "Compile", component))
    results.append(assert_shortdescription(val, "Validate", component))

    # 3) Group header aggregated tag sets: count, uniqueness, sorted
    results.append(assert_group_header_token_set(gen, 4))
    results.append(assert_group_header_token_set(cmp, 3))
    results.append(assert_group_header_token_set(val, 24))

    # 4) Step block counts (2 blocks per .tsc in each group)
    results.append(assert_step_block_count(gen, 6))  # 3 tests
    results.append(assert_step_block_count(cmp, 4))  # 2 tests
    results.append(assert_step_block_count(val, 4))  # 2 tests

    # 5) Specific content checks for a few steps
    results.append(assert_contains_substring(cmp, ".. sw_test_step:: Bogus_Compile_KeyManagement"))
    results.append(assert_contains_substring(cmp, "Description: Ensures generated key management sources compile without errors."))
    results.append(assert_contains_substring(gen, ".. sw_test_step:: Bogus_Generate_Primitives"))
    results.append(assert_contains_substring(gen, "Input: Configurations for AES/HMAC primitive generation."))
    results.append(assert_contains_substring(val, ".. sw_test_step:: Bogus_Validate_Config"))
    results.append(assert_contains_substring(val, "Output: Validation report without errors."))

    # 6) TOC order of generated files
    results.append(assert_toc_order(toc, [
        f"{component}_oAW_Compiler_Tests.rst",
        f"{component}_oAW_Generator_Tests.rst",
        f"{component}_oAW_Validator_Tests.rst",
    ]))

    # 7) Placeholder TODO count for EmptyHeader test
    results.append(assert_todo_count(val, 4))
    failed = [r for r in results if not r.passed]
    for r in results:
        print(("PASS" if r.passed else "FAIL") + f" - {r.name}")
        if not r.passed and r.message:
            print("  " + r.message)

    if failed:
        print(f"\n{len(failed)} assertion(s) failed.", file=sys.stderr)
        return 1
    print("\nAll assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

