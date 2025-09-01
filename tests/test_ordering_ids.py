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
        self.assert_contains(
            self.gen,
            ":tests: BSW_SEC_ModulesHere_Bogus-5048, BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-8001",
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
        self.assert_group_header_token_set(self.gen, 4)
        self.assert_group_header_token_set(self.cmp, 3)
        self.assert_group_header_token_set(self.val, 24)

    def test_step_block_counts(self) -> None:
        """The expected number of step blocks are present per group file."""
        self.assert_step_block_count(self.gen, 6)
        self.assert_step_block_count(self.cmp, 4)
        self.assert_step_block_count(self.val, 4)


if __name__ == "__main__":
    unittest.main()
