from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict

from .utils import report_error, report_warning, ensure_jinja2_installed
from .file_handler import TscHeader


def convert_group_name(group: str, group_name_mappings: Dict[str, str]) -> str:
    lower = group.lower()
    return group_name_mappings.get(lower, group)


def find_toc_rst(component: str, spec_path: Path) -> Path:
    toc_name = f"{component}_component_test.rst"
    candidate = spec_path / toc_name
    if not candidate.exists():
        report_error(candidate, 1, 1301, f"{toc_name} not found in {spec_path}")
    print(f"Table of content rst file:")
    print(f"{candidate}")
    print("")
    return candidate.resolve()


def cleanup_generated_group_files(component: str, toc_path: Path) -> None:
    toc_dir = toc_path.parent
    print(f"Deleted old test specification files:")
    for file in toc_dir.glob(f"{component}_oAW_*.rst"):
        if file == toc_path:
            continue
        try:
            file.unlink()
            print(f"{file}")
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
    component: str, groups: List[str], toc_path: Path, group_name_mappings: Dict[str, str]
) -> None:
    try:
        text = toc_path.read_text(encoding="utf-8")
    except Exception as ex:
        report_error(toc_path, 1, 1303, f"Failed to read TOC file: {ex}")

    appended_lines: List[str] = []
    for group in groups:
        group_conv = convert_group_name(group, group_name_mappings)
        filename = f"{component}_oAW_{group_conv}_Tests.rst"
        appended_lines.append("   " + filename)

    if not text.endswith("\n"):
        text += "\n"
    text += "\n".join(appended_lines) + "\n"
    try:
        toc_path.write_text(text, encoding="utf-8")
    except Exception as ex:
        report_error(toc_path, 1, 1304, f"Failed to write TOC file: {ex}")


def format_tests_value(tags: List[str], delimiter: str, max_width: int, indent_spaces: int) -> str:
    tokens: List[str] = [
        (f"{tag}," if idx < len(tags) - 1 else tag) for idx, tag in enumerate(tags)
    ]
    text = delimiter.join(tokens)
    if len(text) <= max_width:
        return text
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
    if len(lines) <= 1:
        return lines[0]
    indent = " " * indent_spaces
    return ("\n" + indent).join(lines)


def format_multiline_field(label: str, text: str, base_indent_spaces: int = 6) -> List[str]:
    lines: List[str] = []
    indent = " " * base_indent_spaces
    value_indent = " " * (base_indent_spaces + len(label) + 2)
    parts = text.splitlines() if text else [""]
    if parts:
        lines.append(f"{indent}{label}: {parts[0] if parts[0] else ''}")
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
    template_dir: Path,
    group_name_mappings: Dict[str, str],
) -> Path:
    group_conv = convert_group_name(group, group_name_mappings)
    out_path = toc_dir / f"{component}_oAW_{group_conv}_Tests.rst"

    # Aggregate group tags
    all_tags_set = set()
    for _, hdr in parsed:
        for t in hdr.requirements:
            all_tags_set.add(t)
    all_tags = sorted(all_tags_set)
    tests_agg = format_tests_value(all_tags, delimiter=" ", max_width=120, indent_spaces=11)

    # Prepare step contexts
    steps = []
    counter = 1
    for p, hdr in parsed:
        file_display_name = p.stem
        id1 = f"{counter:04d}"
        counter += 1
        id2 = f"{counter:04d}"
        counter += 1

        if hdr.placeholder:
            tsc_name = p.name
            report_warning(
                p,
                hdr.requirements_line,
                2001,
                "Missing Requirements content; emitting TODO in test specification rst file",
            )
            tests_line = (
                f"      :tests: TODO:Update the Requirements field in the header of {tsc_name}"
            )
            report_warning(
                p,
                hdr.desc_line,
                2002,
                "Missing Description content; emitting TODO in test specification rst file",
            )
            desc_lines = format_multiline_field(
                "Description",
                f"TODO:Update the Description field in the header of {tsc_name}",
                base_indent_spaces=6,
            )
            report_warning(
                p,
                hdr.input_line,
                2003,
                "Missing Input content; emitting TODO in test specification rst file",
            )
            input_lines = format_multiline_field(
                "Input",
                f"TODO:Update the Input field in the header of {tsc_name}",
                base_indent_spaces=6,
            )
            report_warning(
                p,
                hdr.output_line,
                2004,
                "Missing Output content; emitting TODO in test specification rst file",
            )
            output_lines = format_multiline_field(
                "Output",
                f"TODO:Update the Output field in the header of {tsc_name}",
                base_indent_spaces=6,
            )
        else:
            if hdr.requirements:
                per_file_tests = format_tests_value(
                    hdr.requirements, delimiter=" ", max_width=120, indent_spaces=14
                )
                tests_line = f"      :tests: {per_file_tests}"
            else:
                report_warning(
                    p,
                    hdr.requirements_line,
                    2001,
                    "Missing Requirements content; emitting TODO in test specification rst file",
                )
                tests_line = (
                    f"      :tests: TODO:Update the Requirements field in the header of {p.name}"
                )

            if hdr.description:
                desc_lines = format_multiline_field(
                    "Description", hdr.description, base_indent_spaces=6
                )
            else:
                report_warning(
                    p,
                    hdr.desc_line,
                    2002,
                    "Missing Description content; emitting TODO in test specification rst file",
                )
                desc_lines = format_multiline_field(
                    "Description",
                    f"TODO:Update the Description field in the header of {p.name}",
                    base_indent_spaces=6,
                )

            if hdr.input_text:
                input_lines = format_multiline_field("Input", hdr.input_text, base_indent_spaces=6)
            else:
                report_warning(
                    p,
                    hdr.input_line,
                    2003,
                    "Missing Input content; emitting TODO in test specification rst file",
                )
                input_lines = format_multiline_field(
                    "Input",
                    f"TODO:Update the Input field in the header of {p.name}",
                    base_indent_spaces=6,
                )

            if hdr.output_text:
                output_lines = format_multiline_field(
                    "Output", hdr.output_text, base_indent_spaces=6
                )
            else:
                report_warning(
                    p,
                    hdr.output_line,
                    2004,
                    "Missing Output content; emitting TODO in test specification rst file",
                )
                output_lines = format_multiline_field(
                    "Output",
                    f"TODO:Update the Output field in the header of {p.name}",
                    base_indent_spaces=6,
                )

        steps.append(
            {
                "file_display_name": file_display_name,
                "id1": id1,
                "id2": id2,
                "tests_line": tests_line,
                "desc_lines": desc_lines,
                "input_lines": input_lines,
                "output_lines": output_lines,
            }
        )

    # Prepare template environment
    ensure_jinja2_installed()
    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
        trim_blocks=False,
        lstrip_blocks=False,
        keep_trailing_newline=True,
    )
    template = env.get_template("oaw_test_group.rst.j2")

    title = f"{group_conv} Test Specification - oAW tests"
    section = f"{component}_oAW_{group_conv}_Tests"
    content = template.render(
        title=title,
        underline="=" * max(len(title), 120),
        component=component,
        group=group,
        group_conv=group_conv,
        section=section,
        tests_agg=tests_agg,
        steps=steps,
    )

    try:
        out_path.write_text(content, encoding="utf-8")
        print(f"{out_path}")
    except Exception as ex:
        report_error(out_path, 1, 1501, f"Failed to write group RST: {ex}")
    return out_path
