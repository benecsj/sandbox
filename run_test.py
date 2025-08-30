#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List


class TestError(AssertionError):
    """Raised when a harness assertion fails."""


def read_config(base_dir: Path) -> tuple[str, Path, Path]:
    config_path = base_dir / "config" / "config.json"
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    component = raw["component"]
    cfg_dir = config_path.parent
    test_path = Path(raw["test_path"]) if Path(raw["test_path"]).is_absolute() else (cfg_dir / raw["test_path"]).resolve()
    spec_path = Path(raw["spec_path"]) if Path(raw["spec_path"]).is_absolute() else (cfg_dir / raw["spec_path"]).resolve()
    return component, test_path, spec_path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_contains_substring(path: Path, substring: str) -> None:
    content = read_text(path)
    if substring not in content:
        raise TestError(f"Expected substring not found in {path}: {substring}")


def assert_regex(path: Path, pattern: str) -> None:
    content = read_text(path)
    if re.search(pattern, content, re.MULTILINE) is None:
        raise TestError(f"Pattern not found in {path}: {pattern}")


def assert_not_regex(path: Path, pattern: str) -> None:
    content = read_text(path)
    if re.search(pattern, content, re.MULTILINE) is not None:
        raise TestError(f"Unexpected pattern present in {path}: {pattern}")


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise TestError(f"Expected file does not exist: {path}")


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


def assert_group_header_token_set(path: Path, expected_count: int) -> None:
    tokens = extract_group_header_tests(path)
    unique = list(dict.fromkeys(tokens))
    is_sorted = tokens == sorted(tokens)
    if not ((len(tokens) == expected_count) and (len(unique) == len(tokens)) and is_sorted):
        raise TestError(
            "Count/unique/sort mismatch: "
            f"count={len(tokens)} expected={expected_count} "
            f"unique={len(unique)} sorted={is_sorted} tokens={tokens[:10]}..."
        )


def count_step_blocks(path: Path) -> int:
    return sum(1 for ln in read_text(path).splitlines() if ln.strip().startswith(".. sw_test_step:: "))


def assert_step_block_count(path: Path, expected: int) -> None:
    count = count_step_blocks(path)
    if count != expected:
        raise TestError(f"Expected {expected} step blocks, found {count}")


def assert_title_line(path: Path, expected_title: str) -> None:
    lines = read_text(path).splitlines()
    first = lines[0] if lines else ""
    if first != expected_title:
        raise TestError(f"Expected first line '{expected_title}', got '{first}'")


def assert_shortdescription(path: Path, group_word: str, component: str) -> None:
    expected = f":tst_shortdescription: Tests for successful {group_word} of {component}"
    assert_contains_substring(path, expected)


def assert_toc_order(toc_path: Path, files_in_order: List[str]) -> None:
    content = read_text(toc_path)
    positions = [content.find(name) for name in files_in_order]
    if not (all(pos >= 0 for pos in positions) and positions == sorted(positions)):
        raise TestError(f"Positions not in order: {positions}")


def assert_todo_count(path: Path, expected: int) -> None:
    count = read_text(path).count("TODO:Update")
    if count != expected:
        raise TestError(f"Expected {expected} TODO lines, found {count}")


def main() -> int:
    from tests.test_generated_spec import CHECKS

    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
            print(f"PASS - {name}")
        except TestError as e:
            failures += 1
            print(f"FAIL - {name}")
            print(f"  {e}")

    if failures:
        print(f"\n{failures} assertion(s) failed.", file=sys.stderr)
        return 1
    print("\nAll assertions passed.")
    return 0


if __name__ == "__main__":
    # Ensure importing this script as "run_test" reuses the same module instance
    sys.modules.setdefault("run_test", sys.modules[__name__])
    sys.exit(main())

