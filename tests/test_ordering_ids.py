"""Tests covering deterministic ordering and sequential ID generation."""

from __future__ import annotations

import re
import unittest

try:
    from tests._base import UnifiedTestCase
except ModuleNotFoundError:
    import os
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    from _base import UnifiedTestCase


class TestOrderingAndIds(UnifiedTestCase):
    """Ordering invariants and test step ID sequences."""

    def test_deterministic_tag_order(self) -> None:
        """Aggregated group tags are rendered in deterministic order."""
        self.assert_contains(
            self.cmp,
            ":tests: BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-6001, BSW_SEC_ModulesHere_Bogus-8001",
        )
        # Generator gains additional tags from the splitting sample; ensure sorted order begins with 1001,1002,1003
        self.assert_contains(
            self.gen,
            ":tests: BSW_SEC_ModulesHere_Bogus-1001, BSW_SEC_ModulesHere_Bogus-1002, BSW_SEC_ModulesHere_Bogus-1003",
        )

    def test_group_ids_present(self) -> None:
        """Group-level :id: fields exist for each generated file."""
        self.assert_regex_file(self.gen, rf"^\s*:id: TS_{self.component}_oAW_Generator_Tests$")
        self.assert_regex_file(self.cmp, rf"^\s*:id: TS_{self.component}_oAW_Compiler_Tests$")
        self.assert_regex_file(self.val, rf"^\s*:id: TS_{self.component}_oAW_Validator_Tests$")

    def test_id_sequences(self) -> None:
        """Per-file test steps have sequential 4-digit IDs starting at 0001."""

        def assert_id_sequence(path, group: str) -> None:
            content = self.read_text(path)
            ids = re.findall(rf":id: TSS_{self.component}_oAW_{group}_Tests_(\d{{4}})", content)
            if not ids:
                raise AssertionError("No step IDs found")
            expected = [f"{i:04d}" for i in range(1, len(ids) + 1)]
            if ids != expected:
                raise AssertionError(f"Expected {expected}, got {ids}")

        assert_id_sequence(self.gen, "Generator")
        assert_id_sequence(self.cmp, "Compiler")
        assert_id_sequence(self.val, "Validator")

    def test_group_header_tag_sets(self) -> None:
        """Aggregated group tag sets are unique, sorted, and of expected size."""
        def extract_group_header_tests(path):
            lines = self.read_text(path).splitlines()
            tokens = []
            collecting = False
            for ln in lines:
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
            parts = [p.strip() for p in text.replace(",", " ").split() if p.strip()]
            return parts

        def assert_group_header_token_set(path, expected_count):
            tokens = extract_group_header_tests(path)
            unique = list(dict.fromkeys(tokens))
            is_sorted = tokens == sorted(tokens)
            if not ((len(tokens) == expected_count) and (len(unique) == len(tokens)) and is_sorted):
                raise AssertionError(
                    f"Count/unique/sort mismatch: count={len(tokens)} expected={expected_count} unique={len(unique)} sorted={is_sorted}"
                )

        assert_group_header_token_set(self.gen, 13)
        assert_group_header_token_set(self.cmp, 3)
        assert_group_header_token_set(self.val, 24)

    def test_step_block_counts(self) -> None:
        """The expected number of step blocks are present per group file."""
        def count_step_blocks(path):
            return sum(
                1 for ln in self.read_text(path).splitlines() if ln.strip().startswith(".. sw_test_step:: ")
            )

        for path, expected in [
            (self.gen, 9),  # 3 existing files * 2 + 1 split file (1 + 2) = 9
            (self.cmp, 4),
            (self.val, 7),  # 1 empty header (2) + 1 split (1 + 4) = 7
        ]:
            count = count_step_blocks(path)
            if count != expected:
                raise AssertionError(f"Expected {expected} step blocks, found {count}")


if __name__ == "__main__":
    unittest.main()
