from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, List, Tuple

import unittest
import run_test as rt

BASE_DIR = Path(__file__).resolve().parent.parent
component, test_path, spec_path = rt.read_config(BASE_DIR)
rt.run_generator(BASE_DIR)

toc = spec_path / f"{component}_component_test.rst"
gen = spec_path / f"{component}_oAW_Generator_Tests.rst"
cmp = spec_path / f"{component}_oAW_Compiler_Tests.rst"
val = spec_path / f"{component}_oAW_Validator_Tests.rst"

CHECKS: List[Tuple[str, Callable[[], None]]] = []


def add_check(name: str, func: Callable[[], None]) -> None:
    CHECKS.append((name, func))


# Existence checks
for p in [toc, gen, cmp, val]:
    add_check(f"exists:{p}", lambda p=p: rt.assert_exists(p))

# TOC links present
add_check("toc-has-generator", lambda: rt.assert_contains_substring(toc, f"{component}_oAW_Generator_Tests.rst"))
add_check("toc-has-compiler", lambda: rt.assert_contains_substring(toc, f"{component}_oAW_Compiler_Tests.rst"))
add_check("toc-has-validator", lambda: rt.assert_contains_substring(toc, f"{component}_oAW_Validator_Tests.rst"))

# Comma-separated tags in headers
add_check("compiler-header-comma", lambda: rt.assert_regex(cmp, r"^\s*:tests: .*?, "))
add_check("generator-header-comma", lambda: rt.assert_regex(gen, r"^\s*:tests: .*?, "))
add_check("validator-header-comma", lambda: rt.assert_regex(val, r"^\s*:tests: .*?, "))

# Header continuation indent in validator
add_check("validator-group-indent-11", lambda: rt.assert_regex(val, r"^\s{11}\S"))
add_check("validator-file-indent-14", lambda: rt.assert_regex(val, r"^\s{14}\S"))

# Placeholder tests for empty header .tsc
add_check(
    "placeholder-tests-line",
    lambda: rt.assert_contains_substring(
        val,
        ":tests: TODO:Update the Requirements field in the header of Bogus_Validate_EmptyHeader.tsc",
    ),
)
add_check(
    "placeholder-description-line",
    lambda: rt.assert_contains_substring(
        val,
        "Description: TODO:Update the Description field in the header of Bogus_Validate_EmptyHeader.tsc",
    ),
)
add_check(
    "placeholder-input-line",
    lambda: rt.assert_contains_substring(
        val,
        "Input: TODO:Update the Input field in the header of Bogus_Validate_EmptyHeader.tsc",
    ),
)
add_check(
    "placeholder-output-line",
    lambda: rt.assert_contains_substring(
        val,
        "Output: TODO:Update the Output field in the header of Bogus_Validate_EmptyHeader.tsc",
    ),
)

# Deterministic ordering
add_check(
    "compiler-tag-order",
    lambda: rt.assert_contains_substring(
        cmp,
        ":tests: BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-6001, BSW_SEC_ModulesHere_Bogus-8001",
    ),
)
add_check(
    "generator-tag-order",
    lambda: rt.assert_contains_substring(
        gen,
        ":tests: BSW_SEC_ModulesHere_Bogus-5048, BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-8001",
    ),
)

# No duplicate TOC links
toc_text = rt.read_text(toc)
for fname in [
    f"{component}_oAW_Generator_Tests.rst",
    f"{component}_oAW_Compiler_Tests.rst",
    f"{component}_oAW_Validator_Tests.rst",
]:
    def check(fname=fname):
        count = toc_text.count(fname)
        if count != 1:
            raise rt.TestError(f"Expected 1 occurrence of {fname}, found {count}")

    add_check(f"toc-unique:{fname}", check)

# Title underline length (120 '=' characters)
def assert_title_underline(path: Path) -> None:
    lines = rt.read_text(path).splitlines()
    if len(lines) < 2:
        raise rt.TestError("File too short for title check")
    if set(lines[1]) != {"="} or len(lines[1]) != 120:
        raise rt.TestError("Expected second line to be 120 '='")


for p in [gen, cmp, val]:
    add_check(f"title-underline:{p.name}", lambda p=p: assert_title_underline(p))


# Section underline (dashes count equals section length)
def assert_section_underline(path: Path, section: str) -> None:
    lines = rt.read_text(path).splitlines()
    for i, ln in enumerate(lines):
        if ln.strip() == section:
            if i + 1 < len(lines) and set(lines[i + 1]) == {"-"} and len(lines[i + 1]) == len(section):
                return
            raise rt.TestError("Dash underline length mismatch")
    raise rt.TestError("Section header not found")


add_check(
    f"section-underline:{gen.name}",
    lambda p=gen, section=f"{component}_oAW_Generator_Tests": assert_section_underline(p, section),
)
add_check(
    f"section-underline:{cmp.name}",
    lambda p=cmp, section=f"{component}_oAW_Compiler_Tests": assert_section_underline(p, section),
)
add_check(
    f"section-underline:{val.name}",
    lambda p=val, section=f"{component}_oAW_Validator_Tests": assert_section_underline(p, section),
)


# Group sw_test block id present
def assert_group_id(path: Path, group: str) -> None:
    pat = rf"^\s*:id: TS_{component}_oAW_{group}_Tests$"
    rt.assert_regex(path, pat)


add_check(f"group-id:{gen.name}", lambda p=gen, g="Generator": assert_group_id(p, g))
add_check(f"group-id:{cmp.name}", lambda p=cmp, g="Compiler": assert_group_id(p, g))
add_check(f"group-id:{val.name}", lambda p=val, g="Validator": assert_group_id(p, g))


# IDs in per-file steps are sequential starting with 0001
def assert_id_sequence(path: Path, group: str) -> None:
    content = rt.read_text(path)
    ids = re.findall(rf":id: TSS_{component}_oAW_{group}_Tests_(\d{{4}})", content)
    if not ids:
        raise rt.TestError("No step IDs found")
    expected = [f"{i:04d}" for i in range(1, len(ids) + 1)]
    if ids != expected:
        raise rt.TestError(f"Expected {expected}, got {ids}")


add_check(f"id-seq:{gen.name}", lambda p=gen, g="Generator": assert_id_sequence(p, g))
add_check(f"id-seq:{cmp.name}", lambda p=cmp, g="Compiler": assert_id_sequence(p, g))
add_check(f"id-seq:{val.name}", lambda p=val, g="Validator": assert_id_sequence(p, g))


# Ensure all :tests: lines use ', '
def assert_comma_space_only(path: Path) -> None:
    bad = []
    for ln in rt.read_text(path).splitlines():
        if ln.strip().startswith(":tests:") and re.search(r",\S", ln):
            bad.append(ln)
    if bad:
        raise rt.TestError(f"Found bad lines: {bad[:2]}")


add_check(f"comma-space:{gen.name}", lambda p=gen: assert_comma_space_only(p))
add_check(f"comma-space:{cmp.name}", lambda p=cmp: assert_comma_space_only(p))
add_check(f"comma-space:{val.name}", lambda p=val: assert_comma_space_only(p))


# Multiline field assertions for the multiline example test in Generator group
add_check(
    "multiline-step-present",
    lambda: rt.assert_contains_substring(gen, ".. sw_test_step:: Bogus_Generate_MultilineExample"),
)
add_check(
    "multiline-desc-line1",
    lambda: rt.assert_contains_substring(
        gen, "Description: This is a multi-line description for the generator test."
    ),
)
add_check(
    "multiline-desc-line2",
    lambda: rt.assert_contains_substring(
        gen, "It spans multiple lines to validate parsing behavior."
    ),
)
add_check(
    "multiline-input-line1",
    lambda: rt.assert_contains_substring(gen, "Input: First line of input description."),
)
add_check(
    "multiline-input-line2",
    lambda: rt.assert_contains_substring(gen, "Second line of input description."),
)
add_check(
    "multiline-output-line1",
    lambda: rt.assert_contains_substring(gen, "Output: First line of output description."),
)
add_check(
    "multiline-output-line2",
    lambda: rt.assert_contains_substring(gen, "Second line of output description."),
)


# Indentation for continuation lines
add_check(
    "indent-desc-cont",
    lambda: rt.assert_regex(gen, r"^\s{19}It spans multiple lines to validate parsing behavior\."),
)
add_check(
    "indent-input-cont",
    lambda: rt.assert_regex(gen, r"^\s{13}Second line of input description\."),
)
add_check(
    "indent-output-cont",
    lambda: rt.assert_regex(gen, r"^\s{14}Second line of output description\."),
)


# Additional explicit assertions
# 1) Exact title lines
add_check(
    "title-line-generator",
    lambda: rt.assert_title_line(gen, "Generator Test Specification - oAW tests"),
)
add_check(
    "title-line-compiler",
    lambda: rt.assert_title_line(cmp, "Compiler Test Specification - oAW tests"),
)
add_check(
    "title-line-validator",
    lambda: rt.assert_title_line(val, "Validator Test Specification - oAW tests"),
)

# 2) Short descriptions per group
add_check("shortdescription-generator", lambda: rt.assert_shortdescription(gen, "Generate", component))
add_check("shortdescription-compiler", lambda: rt.assert_shortdescription(cmp, "Compile", component))
add_check("shortdescription-validator", lambda: rt.assert_shortdescription(val, "Validate", component))

# 3) Group header aggregated tag sets: count, uniqueness, sorted
add_check(f"group-header-tests:{gen.name}", lambda p=gen: rt.assert_group_header_token_set(p, 4))
add_check(f"group-header-tests:{cmp.name}", lambda p=cmp: rt.assert_group_header_token_set(p, 3))
add_check(f"group-header-tests:{val.name}", lambda p=val: rt.assert_group_header_token_set(p, 24))

# 4) Step block counts
add_check(f"step-blocks:{gen.name}", lambda p=gen: rt.assert_step_block_count(p, 6))
add_check(f"step-blocks:{cmp.name}", lambda p=cmp: rt.assert_step_block_count(p, 4))
add_check(f"step-blocks:{val.name}", lambda p=val: rt.assert_step_block_count(p, 4))

# 5) Specific content checks for a few steps
add_check(
    "cmp-step-keymanagement",
    lambda: rt.assert_contains_substring(cmp, ".. sw_test_step:: Bogus_Compile_KeyManagement"),
)
add_check(
    "cmp-desc-keymanagement",
    lambda: rt.assert_contains_substring(
        cmp, "Description: Ensures generated key management sources compile without errors."
    ),
)
add_check(
    "gen-step-primitives",
    lambda: rt.assert_contains_substring(gen, ".. sw_test_step:: Bogus_Generate_Primitives"),
)
add_check(
    "gen-input-primitives",
    lambda: rt.assert_contains_substring(
        gen, "Input: Configurations for AES/HMAC primitive generation."
    ),
)
add_check(
    "val-step-config",
    lambda: rt.assert_contains_substring(val, ".. sw_test_step:: Bogus_Validate_Config"),
)
add_check(
    "val-output-config",
    lambda: rt.assert_contains_substring(val, "Output: Validation report without errors."),
)

# 6) TOC order of generated files
add_check(
    "toc-order",
    lambda: rt.assert_toc_order(
        toc,
        [
            f"{component}_oAW_Compiler_Tests.rst",
            f"{component}_oAW_Generator_Tests.rst",
            f"{component}_oAW_Validator_Tests.rst",
        ],
    ),
)

# 7) Placeholder TODO count for EmptyHeader test
add_check("todo-count", lambda: rt.assert_todo_count(val, 4))


class TestGeneratedSpec(unittest.TestCase):
    pass


def _make_test(func: Callable[[], None]):
    def test(self):
        func()

    return test


for idx, (name, func) in enumerate(CHECKS):
    safe = re.sub(r"\W|^(?=\d)", "_", name)
    setattr(TestGeneratedSpec, f"test_{idx:03d}_{safe}", _make_test(func))


if __name__ == "__main__":
    unittest.main()

