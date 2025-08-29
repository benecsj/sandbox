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


def report_error(file: Path, line: int, code: int, message: str) -> None:
    # Emit without code for VS Code problem matcher: <file>:<line>: (ERROR) <message>
    print(f"{file}:{line}: (ERROR) {message}", file=sys.stderr)
    sys.exit(1)


def report_warning(file: Path, line: int, code: int, message: str) -> None:
    # Emit warning in VS Code problem matcher format; do not exit
    print(f"{file}:{line}: (WARNING) {message}", file=sys.stderr)


def load_config_with_overrides(script_path: Path) -> Config:
    # Parse CLI first to allow selecting an explicit config file
    parser = argparse.ArgumentParser(description="oAW to RST generator")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to config JSON (absolute or relative to script)",
        default=None,
    )
    parser.add_argument("--component", type=str, help="Component name", default=None)
    parser.add_argument(
        "--test_path", type=str, help="Path to test files", default=None
    )
    parser.add_argument(
        "--spec_path", type=str, help="Path to spec files", default=None
    )
    args = parser.parse_args()

    # Determine config.json location
    if args.config:
        specified_path = Path(args.config)
        script_dir = script_path.parent
        config_path: Path = (
            specified_path
            if specified_path.is_absolute()
            else (script_dir / specified_path).resolve()
        )
        config_dir: Path = config_path.parent
        if not config_path.exists():
            report_error(config_path, 1, 1001, f"config file not found: {config_path}")
    else:
        config_dir = script_path.parent
        config_path = config_dir / "config.json"
        if not config_path.exists():
            report_error(
                config_path, 1, 1001, "config.json not found next to oaw_to_rst.py"
            )

    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    component = args.component or raw.get("component")
    test_path_raw = args.test_path or raw.get("test_path")
    spec_path_raw = args.spec_path or raw.get("spec_path")

    if not component or not isinstance(component, str):
        report_error(
            config_path, 1, 1002, "Invalid or missing 'component' in configuration"
        )

    if not test_path_raw or not isinstance(test_path_raw, str):
        report_error(
            config_path, 1, 1003, "Invalid or missing 'test_path' in configuration"
        )

    if not spec_path_raw or not isinstance(spec_path_raw, str):
        report_error(
            config_path, 1, 1004, "Invalid or missing 'spec_path' in configuration"
        )

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
        report_error(
            config.test_path,
            1,
            1101,
            "'test_path' does not exist or is not a directory",
        )
    if not config.spec_path.exists() or not config.spec_path.is_dir():
        report_error(
            config.spec_path,
            1,
            1102,
            "'spec_path' does not exist or is not a directory",
        )


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


def group_tsc_files_by_group(
    component: str, tsc_files: List[Path]
) -> Dict[str, List[Path]]:
    groups: Dict[str, List[Path]] = {}
    for file_path in tsc_files:
        stem = file_path.stem
        parts = stem.split("_")
        if len(parts) < 3 or parts[0] != component:
            report_error(file_path, 1, 1201, "No valid group token in filename")
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
        report_error(candidate, 1, 1301, f"{toc_name} not found in {config.spec_path}")
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
            report_error(file, 1, 1302, f"Failed to delete file: {ex}")


def remove_generated_lines_from_toc(component: str, toc_path: Path) -> None:
    try:
        text = toc_path.read_text(encoding="utf-8")
    except Exception as ex:
        report_error(toc_path, 1, 1303, f"Failed to read TOC file: {ex}")
    lines = text.splitlines()
    prefix = f"{component}_oAW_"
    filtered = [ln for ln in lines if not ln.lstrip().startswith(prefix)]
    try:
        toc_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")
    except Exception as ex:
        report_error(toc_path, 1, 1304, f"Failed to write TOC file: {ex}")


def append_group_links_to_toc(
    component: str, groups: List[str], toc_path: Path
) -> None:
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
    desc_line: int
    input_line: int
    output_line: int
    requirements_line: int


def parse_tsc_header(path: Path) -> TscHeader:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as ex:
        report_error(path, 1, 1401, f"Failed to read .tsc file: {ex}")

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
    seen_tokens: set[str] = set()
    header_lines: Dict[str, int] = {}

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
            header_match = re.fullmatch(
                r"(?i)(description|input|output|requirements)\s*", content
            )
            if header_match:
                name = header_match.group(1).lower()
                if (
                    order_index >= len(expected_order)
                    or name != expected_order[order_index]
                ):
                    report_error(
                        path,
                        idx + 1,
                        1402,
                        f"Unexpected or out-of-order section '{name}'",
                    )
                current = name
                order_index += 1
                seen_tokens.add(name)
                header_lines[name] = idx + 1
            else:
                if current is None:
                    report_error(
                        path, idx + 1, 1403, "Header must start with 'Description'"
                    )
                sections[current].append(content.rstrip())
            idx += 1
            continue
        else:
            # First non-comment ends header block
            if order_index == 0:
                report_error(path, 1, 1404, "Header missing")
            break

    # Ensure all required header tokens are present (content may be empty)
    missing_tokens = [tok for tok in expected_order if tok not in seen_tokens]
    if missing_tokens:
        report_error(
            path,
            1,
            1405,
            f"Missing header section(s): {', '.join(t.capitalize() for t in missing_tokens)}",
        )

    # Determine if this is a placeholder-only header (all sections present but empty)
    all_present_empty = all(len(sections[key]) == 0 for key in expected_order)

    # Post-process requirements: split on commas and whitespace, dedupe and sort
    req_line = " ".join(sections["requirements"]).replace(",", " ")
    tags_raw = [t.strip() for t in req_line.split() if t.strip()]
    tags = sorted(set(tags_raw))

    # Allow empty requirements if other fields are present; TODO placeholders will be generated later

    return TscHeader(
        description="\n".join(sections["description"]).strip(),
        input_text="\n".join(sections["input"]).strip(),
        output_text="\n".join(sections["output"]).strip(),
        requirements=tags,
        placeholder=all_present_empty,
        desc_line=header_lines.get("description", 1),
        input_line=header_lines.get("input", 1),
        output_line=header_lines.get("output", 1),
        requirements_line=header_lines.get("requirements", 1),
    )


def format_tests_value(
    tags: List[str],
    delimiter: str = " ",
    max_width: int = 120,
    indent_spaces: int = 11,
) -> str:
    # Build tokens so that every tag except the last has a trailing comma
    tokens: List[str] = [
        (f"{tag}," if idx < len(tags) - 1 else tag) for idx, tag in enumerate(tags)
    ]
    text = delimiter.join(tokens)
    if len(text) <= max_width:
        return text
    # Create wrapped lines with specific indentation for subsequent lines
    lines: List[str] = []
    current_line = ""
    for token in tokens:
        candidate = token if not current_line else current_line + delimiter + token
        if len(candidate) > max_width and current_line:
            lines.append(current_line)
            current_line = token
        else:
            current_line = candidate
    if current_line:
        lines.append(current_line)
    # Indent continuation lines
    if len(lines) <= 1:
        return lines[0]
    indent = " " * indent_spaces
    return ("\n" + indent).join(lines)


def format_multiline_field(
    label: str, text: str, base_indent_spaces: int = 6
) -> List[str]:
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
    tests_agg = format_tests_value(
        all_tags, delimiter=" ", max_width=120, indent_spaces=11
    )

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
    lines.append(
        f"   :tst_shortdescription: Tests for successful {group} of {component}"
    )
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
            report_warning(p, hdr.requirements_line, 2001, "Missing Requirements content; emitting TODO in RST")
            lines.append(
                f"      :tests: TODO:Update the Requirements field in the header of {tsc_name}"
            )
            lines.append("      ")
            report_warning(p, hdr.desc_line, 2002, "Missing Description content; emitting TODO in RST")
            lines.extend(
                format_multiline_field(
                    "Description",
                    f"TODO:Update the Description field in the header of {tsc_name}",
                    base_indent_spaces=6,
                )
            )
            lines.append("      ")
            report_warning(p, hdr.input_line, 2003, "Missing Input content; emitting TODO in RST")
            lines.extend(
                format_multiline_field(
                    "Input",
                    f"TODO:Update the Input field in the header of {tsc_name}",
                    base_indent_spaces=6,
                )
            )
            lines.append("")
            report_warning(p, hdr.output_line, 2004, "Missing Output content; emitting TODO in RST")
            lines.extend(
                format_multiline_field(
                    "Output",
                    f"TODO:Update the Output field in the header of {tsc_name}",
                    base_indent_spaces=6,
                )
            )
        else:
            # Per-file tags: if empty, emit TODO; otherwise, format with trailing commas and 14-space continuation
            if hdr.requirements:
                per_file_tests = format_tests_value(
                    hdr.requirements, delimiter=" ", max_width=120, indent_spaces=14
                )
                lines.append(f"      :tests: {per_file_tests}")
            else:
                report_warning(p, hdr.requirements_line, 2001, "Missing Requirements content; emitting TODO in RST")
                lines.append(
                    f"      :tests: TODO:Update the Requirements field in the header of {p.name}"
                )
            lines.append("      ")
            if hdr.description:
                lines.extend(
                    format_multiline_field("Description", hdr.description, base_indent_spaces=6)
                )
            else:
                report_warning(p, hdr.desc_line, 2002, "Missing Description content; emitting TODO in RST")
                lines.extend(
                    format_multiline_field(
                        "Description",
                        f"TODO:Update the Description field in the header of {p.name}",
                        base_indent_spaces=6,
                    )
                )
            lines.append("      ")
            if hdr.input_text:
                lines.extend(
                    format_multiline_field("Input", hdr.input_text, base_indent_spaces=6)
                )
            else:
                report_warning(p, hdr.input_line, 2003, "Missing Input content; emitting TODO in RST")
                lines.extend(
                    format_multiline_field(
                        "Input",
                        f"TODO:Update the Input field in the header of {p.name}",
                        base_indent_spaces=6,
                    )
                )
            lines.append("")
            if hdr.output_text:
                lines.extend(
                    format_multiline_field("Output", hdr.output_text, base_indent_spaces=6)
                )
            else:
                report_warning(p, hdr.output_line, 2004, "Missing Output content; emitting TODO in RST")
                lines.extend(
                    format_multiline_field(
                        "Output",
                        f"TODO:Update the Output field in the header of {p.name}",
                        base_indent_spaces=6,
                    )
                )
        lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    try:
        out_path.write_text(content, encoding="utf-8")
        print(f"Generated group RST: {out_path}")
    except Exception as ex:
        report_error(out_path, 1, 1501, f"Failed to write group RST: {ex}")
    return out_path


def parse_all_headers(
    tsc_file_groups: Dict[str, List[Path]],
) -> Dict[str, List[Tuple[Path, TscHeader]]]:
    parsed_groups: Dict[str, List[Tuple[Path, TscHeader]]] = {}
    for group, files in tsc_file_groups.items():
        parsed_list: List[Tuple[Path, TscHeader]] = []
        for p in files:
            hdr = parse_tsc_header(
                p
            )  # will exit on error; validates before any RST modifications
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
