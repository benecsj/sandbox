"""Tests for splitting requirements across multiple numeric steps."""

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


class TestSplittingBehavior(UnifiedTestCase):
    """Verify that files with >7 tags are split into multiple steps."""

    def test_split_into_two_steps(self) -> None:
        # Ensure the file anchor exists
        self.assert_contains(self.gen, ".. sw_test_step:: Bogus_Generate_SplitTags")

        content = self.read_text(self.gen)

        # Isolate the block corresponding to Bogus_Generate_SplitTags
        file_anchor = re.search(r"^\s*\.\. sw_test_step:: Bogus_Generate_SplitTags\s*$", content, re.MULTILINE)
        self.assertIsNotNone(file_anchor)
        start = file_anchor.end()
        next_file = re.search(r"^\s*\.\. sw_test_step:: Bogus_\S+\s*$", content[start:], re.MULTILINE)
        end = start + next_file.start() if next_file else len(content)
        segment = content[start:end]

        # Collect the numeric step blocks following the file anchor within this segment
        # We expect two numeric steps: 1 and 2
        step_headers = re.findall(r"^\s*\.\. sw_test_step:: (\d+)\s*$", segment, re.MULTILINE)
        self.assertTrue("1" in step_headers and "2" in step_headers)

        # Check that step 1 contains seven tags and step 2 contains two
        def collect_tests_after_step(step_number: int) -> str:
            pattern = rf"^\s*\.\. sw_test_step:: {step_number}\s*$([\s\S]*?)^(?:\s*\.\. sw_test_step:: |\Z)"
            m = re.search(pattern, segment, re.MULTILINE)
            return m.group(1) if m else ""

        step1 = collect_tests_after_step(1)
        step2 = collect_tests_after_step(2)

        # Extract tags lines
        def extract_tags(block: str) -> list[str]:
            lines = []
            for ln in block.splitlines():
                if ln.strip().startswith(":tests:"):
                    lines.append(ln.split(":tests:", 1)[1].strip())
                elif ln.startswith("              ") and ln.strip():  # 14 spaces continuation
                    lines.append(ln.strip())
                elif lines and ln.strip() == "":
                    break
            text = " ".join(lines)
            return [p.strip() for p in text.replace(",", " ").split() if p.strip()]

        self.assertEqual(len(extract_tags(step1)), 7)
        self.assertEqual(len(extract_tags(step2)), 2)


if __name__ == "__main__":
    unittest.main()

