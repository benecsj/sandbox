#!/usr/bin/env python3
"""
oAWToRst (oaw_to_rst.py)

Generates and updates RST documentation for oAW tests based on .tsc files.
See specification in specification.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap
from typing import Dict, List, Tuple


@dataclass
class Config:
    component: str
    test_path: Path
    spec_path: Path


def load_config_with_overrides(script_path: Path) -> Config:
    config_dir: Path = script_path.parent
    config_path: Path = config_dir / "config.json"
    if not config_path.exists():
        print("ERROR config.json not found next to oaw_to_rst.py", file=sys.stderr)
        sys.exit(1)

    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    parser = argparse.ArgumentParser(description="oAW to RST generator")
    parser.add_argument("--component", type=str, help="Component name", default=None)
    parser.add_argument("--test_path", type=str, help="Path to test files", default=None)
    parser.add_argument("--spec_path", type=str, help="Path to spec files", default=None)
    args = parser.parse_args()

    component = args.component or raw.get("component")
    test_path_raw = args.test_path or raw.get("test_path")
    spec_path_raw = args.spec_path or raw.get("spec_path")

    if not component or not isinstance(component, str):
        print("ERROR Invalid or missing 'component' in configuration", file=sys.stderr)
        sys.exit(1)

    if not test_path_raw or not isinstance(test_path_raw, str):
        print("ERROR Invalid or missing 'test_path' in configuration", file=sys.stderr)
        sys.exit(1)

    if not spec_path_raw or not isinstance(spec_path_raw, str):
        print("ERROR Invalid or missing 'spec_path' in configuration", file=sys.stderr)
        sys.exit(1)

    test_path = Path(test_path_raw)
    spec_path = Path(spec_path_raw)

    if not test_path.is_absolute():
        test_path = (config_dir / test_path).resolve()
    if not spec_path.is_absolute():
        spec_path = (config_dir / spec_path).resolve()

    print(f"Component: {component}")
    print(f"Test path: {test_path}")
    print(f"Spec path: {spec_path}")

    return Config(component=component, test_path=test_path, spec_path=spec_path)


def validate_paths(config: Config) -> None:
    if not config.test_path.exists() or not config.test_path.is_dir():
        print(f"ERROR 'test_path' does not exist: {config.test_path}", file=sys.stderr)
        sys.exit(1)
    if not config.spec_path.exists() or not config.spec_path.is_dir():
        print(f"ERROR 'spec_path' does not exist: {config.spec_path}", file=sys.stderr)
        sys.exit(1)


def discover_tsc_files(config: Config) -> List[Path]:
    prefix = f"{config.component}_"
    results: List[Path] = []
    for path in config.test_path.rglob("*.tsc"):
        if path.name.startswith(prefix):
            results.append(path.resolve())
    # Sort by full path string for deterministic ordering across directories
    results.sort(key=lambda p: str(p))
    for p in results:
        print(str(p))
    if not results:
        print(f"No oAW tests found for {config.component}.")
    return results


def group_tsc_files_by_group(component: str, tsc_files: List[Path]) -> Dict[str, List[Path]]:
    groups: Dict[str, List[Path]] = {}
    for file_path in tsc_files:
        stem = file_path.stem
        parts = stem.split("_")
        if len(parts) < 3 or parts[0] != component:
            print(f"ERROR No valid group token in filename: {file_path}", file=sys.stderr)
            sys.exit(1)
        group = parts[1]
        groups.setdefault(group, []).append(file_path)
    # Sort deterministically
    for group_name in groups:
        groups[group_name].sort(key=lambda p: str(p))
    # Return dict with sorted keys to keep deterministic iteration order
    return dict(sorted(groups.items(), key=lambda kv: kv[0]))


def convert_group_name(group: str) -> str:
    lower = group.lower()
    if lower == "generate":
        return "Generator"
    if lower == "compile":
        return "Compiler"
    if lower == "validate":
        return "Validator"
    return group


def find_toc_rst(config: Config) -> Path:
    toc_name = f"{config.component}_component_test.rst"
    candidate = config.spec_path / toc_name
    if not candidate.exists():
        print(f"ERROR {toc_name} not found in {config.spec_path}", file=sys.stderr)
        sys.exit(1)
    print(f"TOC RST: {candidate} (found)")
    return candidate.resolve()


def cleanup_generated_group_files(component: str, toc_path: Path) -> None:
    toc_dir = toc_path.parent
    for file in toc_dir.glob(f"{component}_oAW_*.rst"):
        if file == toc_path:
            continue
        try:
            file.unlink()
            print(f"Deleted old generated file: {file}")
        except Exception as ex:
            print(f"ERROR Failed to delete file {file}: {ex}", file=sys.stderr)
            sys.exit(1)


def remove_generated_lines_from_toc(component: str, toc_path: Path) -> None:
    try:
        text = toc_path.read_text(encoding="utf-8")
    except Exception as ex:
        print(f"ERROR Failed to read TOC file {toc_path}: {ex}", file=sys.stderr)
        sys.exit(1)
    lines = text.splitlines()
    prefix = f"{component}_oAW_"
    filtered = [ln for ln in lines if not ln.lstrip().startswith(prefix)]
    try:
        toc_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")
    except Exception as ex:
        print(f"ERROR Failed to write TOC file {toc_path}: {ex}", file=sys.stderr)
        sys.exit(1)


def append_group_links_to_toc(component: str, groups: List[str], toc_path: Path) -> None:
    try:
        text = toc_path.read_text(encoding="utf-8")
    except Exception as ex:
        print(f"ERROR Failed to read TOC file {toc_path}: {ex}", file=sys.stderr)
        sys.exit(1)

    appended_lines: List[str] = []
    for group in groups:
        group_conv = convert_group_name(group)
        filename = f"{component}_oAW_{group_conv}_Tests.rst"
        appended_lines.append(filename)

    # Always append at the end for simplicity and determinism
    if not text.endswith("\n"):
        text += "\n"
    text += "\n".join(appended_lines) + "\n"
    try:
        toc_path.write_text(text, encoding="utf-8")
    except Exception as ex:
        print(f"ERROR Failed to write TOC file {toc_path}: {ex}", file=sys.stderr)
        sys.exit(1)


@dataclass
class TscHeader:
    description: str
    input_text: str
    output_text: str
    requirements: List[str]
    placeholder: bool


def parse_tsc_header(path: Path) -> TscHeader:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as ex:
        print(f"ERROR Failed to read .tsc file {path}: {ex}", file=sys.stderr)
        sys.exit(1)

    # Normalize newlines and split
    lines = text.splitlines()
    # Only consider leading commented block
    idx = 0
    # Helper to strip '//' and optional single space
    def strip_comment_prefix(s: str) -> str:
        if not s.lstrip().startswith("//"):
            return s
        s2 = s.lstrip()[2:]
        if s2.startswith(" "):
            s2 = s2[1:]
        return s2

    # States
    sections = {"description": [], "input": [], "output": [], "requirements": []}
    current: str | None = None
    expected_order = ["description", "input", "output", "requirements"]
    order_index = 0

    while idx < len(lines):
        raw = lines[idx]
        if not raw.strip():
            # Empty line ends header once some content parsed
            if order_index > 0:
                break
            idx += 1
            continue
        if raw.lstrip().startswith("//"):
            content = strip_comment_prefix(raw)
            header_match = re.fullmatch(r"(?i)(description|input|output|requirements)\s*", content)
            if header_match:
                name = header_match.group(1).lower()
                if order_index >= len(expected_order) or name != expected_order[order_index]:
                    print(f"ERROR Unexpected or out-of-order section '{name}' in {path}", file=sys.stderr)
                    sys.exit(1)
                current = name
                order_index += 1
            else:
                if current is None:
                    print(f"ERROR Header must start with 'Description' in {path}", file=sys.stderr)
                    sys.exit(1)
                sections[current].append(content.rstrip())
            idx += 1
            continue
        else:
            # First non-comment ends header block
            if order_index == 0:
                print(f"ERROR Header missing in {path}", file=sys.stderr)
                sys.exit(1)
            break

    # Determine if this is a placeholder-only header (all sections present but empty)
    all_present_empty = all(len(sections[key]) == 0 for key in expected_order)

    # Validate required sections when not a placeholder-only header
    if not all_present_empty:
        for key in expected_order:
            if not sections[key]:
                print(f"ERROR Missing {key.capitalize()} in header: {path}", file=sys.stderr)
                sys.exit(1)

    # Post-process requirements: split on commas and whitespace, dedupe and sort
    req_line = " ".join(sections["requirements"]).replace(",", " ")
    tags_raw = [t.strip() for t in req_line.split() if t.strip()]
    tags = sorted(set(tags_raw))

    if not tags and not all_present_empty:
        print(f"ERROR Requirements must contain at least one tag in {path}", file=sys.stderr)
        sys.exit(1)

    return TscHeader(
        description="\n".join(sections["description"]).strip(),
        input_text="\n".join(sections["input"]).strip(),
        output_text="\n".join(sections["output"]).strip(),
        requirements=tags,
        placeholder=all_present_empty,
    )


def format_tests_value(tags: List[str], delimiter: str = ", ", max_width: int = 120, indent_spaces: int = 11) -> str:
    text = delimiter.join(tags)
    if len(text) <= max_width:
        return text
    # Create wrapped lines with specific indentation for subsequent lines
    lines: List[str] = []
    current_line = ""
    for tag in tags:
        candidate = tag if not current_line else current_line + delimiter + tag
        if len(candidate) > max_width and current_line:
            lines.append(current_line)
            current_line = tag
        else:
            current_line = candidate
    if current_line:
        lines.append(current_line)
    # Indent continuation lines
    if len(lines) <= 1:
        return lines[0]
    indent = " " * indent_spaces
    return ("\n" + indent).join(lines)


def format_multiline_field(label: str, text: str, base_indent_spaces: int = 6) -> List[str]:
    lines: List[str] = []
    indent = " " * base_indent_spaces
    value_indent = " " * (base_indent_spaces + len(label) + 2)  # account for ': '
    parts = text.splitlines() if text else [""]
    if parts:
        # First line with label
        lines.append(f"{indent}{label}: {parts[0] if parts[0] else ''}")
        # Continuation lines aligned under value start
        for cont in parts[1:]:
            lines.append(f"{value_indent}{cont}")
    else:
        lines.append(f"{indent}{label}:")
    return lines


def generate_group_rst(
    component: str,
    group: str,
    parsed: List[Tuple[Path, TscHeader]],
    toc_dir: Path,
) -> Path:
    group_conv = convert_group_name(group)
    out_path = toc_dir / f"{component}_oAW_{group_conv}_Tests.rst"

    # Accumulate tags from pre-parsed headers
    all_tags_set = set()
    for _, hdr in parsed:
        for t in hdr.requirements:
            all_tags_set.add(t)

    all_tags = sorted(all_tags_set)
    tests_agg = format_tests_value(all_tags, delimiter=", ", max_width=120, indent_spaces=11)

    # Build content
    lines: List[str] = []
    title = f"{group_conv} Test Specification - oAW tests"
    lines.append(title)
    lines.append("=" * max(len(title), 120))
    lines.append("")
    section = f"{component}_oAW_{group_conv}_Tests"
    lines.append(section)
    lines.append("-" * len(section))
    lines.append("")
    lines.append(f".. sw_test:: {component}_oAW_{group_conv}_Tests")
    lines.append(f"   :id: TS_{component}_oAW_{group_conv}_Tests")
    lines.append(f"   :tst_shortdescription: Tests for successful {group} of {component}")
    lines.append("   :tst_level: Component Requirement Test")
    lines.append(f"   :tst_designdoc: {component}_VerificationDocumentation.docx")
    lines.append("   :tst_envconditions: oAW on PC")
    lines.append("   :tst_method: Interface tests/API tests")
    lines.append("   :tst_preparation: nothing specific")
    lines.append("   :tst_type: Manual")
    lines.append("   :tst_env: Generator-Test")
    lines.append(f"   :tests: {tests_agg}")
    lines.append("")
    lines.append("   See descriptions below")
    lines.append("")

    # Two steps per file with incrementing IDs
    counter = 1
    for p, hdr in parsed:
        file_display_name = p.stem
        id1 = f"{counter:04d}"
        counter += 1
        id2 = f"{counter:04d}"
        counter += 1

        lines.append(f"   .. sw_test_step:: {file_display_name}")
        lines.append(f"      :id: TSS_{component}_oAW_{group_conv}_Tests_{id1}")
        lines.append("      :collapse: true")
        lines.append("")
        lines.append("   .. sw_test_step:: 1")
        lines.append(f"      :id: TSS_{component}_oAW_{group_conv}_Tests_{id2}")
        lines.append("      :collapse: true")
        if hdr.placeholder:
            tsc_name = p.name
            lines.append(f"      :tests: TODO:Update the Requirements field in the header of {tsc_name}")
            lines.append("      ")
            lines.extend(format_multiline_field("Description", f"TODO:Update the Description field in the header of {tsc_name}", base_indent_spaces=6))
            lines.append("      ")
            lines.extend(format_multiline_field("Input", f"TODO:Update the Input field in the header of {tsc_name}", base_indent_spaces=6))
            lines.append("")
            lines.extend(format_multiline_field("Output", f"TODO:Update the Output field in the header of {tsc_name}", base_indent_spaces=6))
        else:
            # Per-file tags already sorted in parse_tsc_header; per requirement indent continuation by 14 spaces
            per_file_tests = format_tests_value(hdr.requirements, delimiter=", ", max_width=120, indent_spaces=14)
            lines.append(f"      :tests: {per_file_tests}")
            lines.append("      ")
            lines.extend(format_multiline_field("Description", hdr.description, base_indent_spaces=6))
            lines.append("      ")
            lines.extend(format_multiline_field("Input", hdr.input_text, base_indent_spaces=6))
            lines.append("")
            lines.extend(format_multiline_field("Output", hdr.output_text, base_indent_spaces=6))
        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    try:
        out_path.write_text(content, encoding="utf-8")
        print(f"Generated group RST: {out_path}")
    except Exception as ex:
        print(f"ERROR Failed to write group RST {out_path}: {ex}", file=sys.stderr)
        sys.exit(1)
    return out_path


def parse_all_headers(tsc_file_groups: Dict[str, List[Path]]) -> Dict[str, List[Tuple[Path, TscHeader]]]:
    parsed_groups: Dict[str, List[Tuple[Path, TscHeader]]] = {}
    for group, files in tsc_file_groups.items():
        parsed_list: List[Tuple[Path, TscHeader]] = []
        for p in files:
            hdr = parse_tsc_header(p)  # will exit on error; validates before any RST modifications
            parsed_list.append((p, hdr))
        parsed_groups[group] = parsed_list
    return parsed_groups


def main() -> int:
    script_path = Path(__file__).resolve()
    config = load_config_with_overrides(script_path)
    validate_paths(config)

    tsc_files = discover_tsc_files(config)
    if not tsc_files:
        return 0

    tsc_file_groups = group_tsc_files_by_group(config.component, tsc_files)
    # Parse and validate ALL headers before any RST file is modified
    parsed_groups = parse_all_headers(tsc_file_groups)

    toc_path = find_toc_rst(config)

    cleanup_generated_group_files(config.component, toc_path)
    remove_generated_lines_from_toc(config.component, toc_path)
    append_group_links_to_toc(config.component, list(tsc_file_groups.keys()), toc_path)

    toc_dir = toc_path.parent
    for group_name, parsed_list in parsed_groups.items():
        generate_group_rst(config.component, group_name, parsed_list, toc_dir)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

