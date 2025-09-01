"""Generate reStructuredText files from parsed test specifications."""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
from textwrap import TextWrapper
from .utils import report_error, report_warning
from .file_handler import TscHeader
from jinja2 import Environment, FileSystemLoader


def convert_group_name(group: str, group_name_mappings: Dict[str, str]) -> str:
    """Map ``group`` to its configured display name."""

    lower = group.lower()
    return group_name_mappings.get(lower, group)


def find_toc_rst(component: str, spec_path: Path) -> Path:
    """Locate the component's TOC RST file under ``spec_path`` (recursive).

    Preference order when multiple matches exist:
    1) File located at the root of ``spec_path``
    2) Shallowest relative depth (fewest path parts)
    3) Lexicographically smallest path for deterministic selection
    """

    toc_name = f"{component}_component_test.rst"
    root_candidate = spec_path / toc_name

    # Prefer the TOC file at the root if it exists
    if root_candidate.exists():
        selected = root_candidate
    else:
        # Search recursively for any matching TOC file
        matches = list(spec_path.rglob(toc_name))
        if not matches:
            report_error(root_candidate, 1, f"{toc_name} not found under {spec_path} (recursive search)")

        # If there are multiple matches, pick the shallowest; tie-break lexicographically
        def sort_key(p: Path) -> tuple[int, str]:
            rel = p.relative_to(spec_path)
            return (len(rel.parts), str(p))

        matches.sort(key=sort_key)
        selected = matches[0]

    print("Table of content rst file:")
    print(f"{selected}")
    print("")
    return selected.resolve()


def cleanup_generated_group_files(component: str, toc_path: Path) -> None:
    """Remove previously generated group files to avoid stale data."""

    toc_dir = toc_path.parent
    print("Deleted old test specification files:")
    for file in toc_dir.glob(f"{component}_oAW_*.rst"):
        if file == toc_path:
            continue
        try:
            file.unlink()
            print(f"{file}")
        except Exception as ex:
            report_error(file, 1, f"Failed to delete file: {ex}")


def remove_generated_lines_from_toc(component: str, toc_path: Path) -> None:
    """Strip previously added group entries from the TOC file."""

    try:
        text = toc_path.read_text(encoding="utf-8")
    except Exception as ex:
        report_error(toc_path, 1, f"Failed to read TOC file: {ex}")
    lines = text.splitlines()
    prefix = f"{component}_oAW_"
    filtered = [ln for ln in lines if not ln.lstrip().startswith(prefix)]
    try:
        toc_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")
    except Exception as ex:
        report_error(toc_path, 1, f"Failed to write TOC file: {ex}")


def append_group_links_to_toc(
    component: str, groups: List[str], toc_path: Path, group_name_mappings: Dict[str, str]
) -> None:
    """Append group-specific RST links to the TOC file."""

    try:
        text = toc_path.read_text(encoding="utf-8")
    except Exception as ex:
        report_error(toc_path, 1, f"Failed to read TOC file: {ex}")

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
        report_error(toc_path, 1, f"Failed to write TOC file: {ex}")


def format_tests_value(tags: List[str], delimiter: str, max_width: int, indent_spaces: int) -> str:
    """Wrap requirement tags into a single formatted string."""

    if not tags:
        return ""
    tokens = [f"{tag}," for tag in tags[:-1]] + [tags[-1]]
    text = delimiter.join(tokens)
    wrapper = TextWrapper(
        width=max_width,
        subsequent_indent=" " * indent_spaces,
        break_long_words=False,
    )
    return wrapper.fill(text)


def format_multiline_field(label: str, text: str, base_indent_spaces: int = 6) -> List[str]:
    """Format a header field into indented lines for RST output."""

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
    """Render the RST file for a specific group of tests."""

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

    def build_tests_line(path: Path, header: TscHeader) -> str:
        if header.requirements:
            per_file_tests = format_tests_value(
                header.requirements, delimiter=" ", max_width=120, indent_spaces=14
            )
            return f"      :tests: {per_file_tests}"
        report_warning(
            path,
            header.requirements_line,
            "Missing Requirements content; emitting TODO in test specification rst file",
        )
        return f"      :tests: TODO:Update the Requirements field in the header of {path.name}"

    def build_field_lines(label: str, content: str, line_no: int, path: Path) -> List[str]:
        if content:
            return format_multiline_field(label, content, base_indent_spaces=6)
        report_warning(
            path,
            line_no,
            f"Missing {label} content; emitting TODO in test specification rst file",
        )
        return format_multiline_field(
            label,
            f"TODO:Update the {label} field in the header of {path.name}",
            base_indent_spaces=6,
        )

    for p, hdr in parsed:
        file_display_name = p.stem
        id1 = f"{counter:04d}"
        counter += 1
        id2 = f"{counter:04d}"
        counter += 1

        tests_line = build_tests_line(p, hdr)
        desc_lines = build_field_lines("Description", hdr.description, hdr.desc_line, p)
        input_lines = build_field_lines("Input", hdr.input_text, hdr.input_line, p)
        output_lines = build_field_lines("Output", hdr.output_text, hdr.output_line, p)

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
        report_error(out_path, 1, f"Failed to write group RST: {ex}")
    return out_path
