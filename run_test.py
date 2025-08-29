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
    results.append(assert_regex(val, r"^\s{11}BSW_SWCS_CryptoDriver_Crypto-"))

    # Per-file continuation indent = 14 spaces exists in validator (for long tag list)
    results.append(assert_regex(val, r"^\s{14}BSW_SWCS_CryptoDriver_Crypto-"))

    # Placeholder tests for empty header .tsc
    results.append(assert_contains_substring(val, ":tests: TODO:Update the Requirements field in the header of Crypto_Validate_EmptyHeader.tsc"))
    results.append(assert_contains_substring(val, "Description: TODO:Update the Description field in the header of Crypto_Validate_EmptyHeader.tsc"))
    results.append(assert_contains_substring(val, "Input: TODO:Update the Input field in the header of Crypto_Validate_EmptyHeader.tsc"))
    results.append(assert_contains_substring(val, "Output: TODO:Update the Output field in the header of Crypto_Validate_EmptyHeader.tsc"))

    # Deterministic ordering: Compiler aggregated tags in ascending order
    results.append(assert_contains_substring(cmp, ":tests: BSW_SWCS_CryptoDriver_Crypto-5770, BSW_SWCS_CryptoDriver_Crypto-6001, BSW_SWCS_CryptoDriver_Crypto-8001"))
    results.append(assert_contains_substring(gen, ":tests: BSW_SWCS_CryptoDriver_Crypto-5048, BSW_SWCS_CryptoDriver_Crypto-5770, BSW_SWCS_CryptoDriver_Crypto-8001"))

    # Summarize
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

