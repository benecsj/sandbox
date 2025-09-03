"""Generate reStructuredText files from parsed test specifications."""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
from textwrap import TextWrapper
try:
    from jinja2 import Environment, FileSystemLoader  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    Environment = None  # type: ignore
    FileSystemLoader = None  # type: ignore
from .utils import report_error, report_warning
from .file_handler import TscHeader


def convert_group_name(group: str, group_name_mappings: Dict[str, str]) -> str:
    """Map ``group`` to its configured display name."""

    lower = group.lower()
    return group_name_mappings.get(lower, group)


def find_toc_rst(component: str, spec_path: Path) -> Path:
    """Locate the component's TOC RST file by searching recursively.

    Searches depth-first under ``spec_path`` for ``{component}_component_test.rst``.
    Raises an error if not found.
    """

    toc_name = f"{component}_component_test.rst"

    # First, check the exact path for backward compatibility
    candidate = spec_path / toc_name
    if candidate.exists():
        found = candidate
    else:
        # Search recursively under spec_path
        matches = list(spec_path.rglob(toc_name))
        if not matches:
            report_error(candidate, 1, f"{toc_name} not found under {spec_path}")
        # Prefer the first match (Path.rglob returns in directory order)
        found = matches[0]

    print("Table of content rst file:")
    print(f"{found}")
    print("")
    return found.resolve()


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

        # Build common field lines once
        desc_lines_full = build_field_lines("Description", hdr.description, hdr.desc_line, p)
        input_lines_full = build_field_lines("Input", hdr.input_text, hdr.input_line, p)
        output_lines_full = build_field_lines("Output", hdr.output_text, hdr.output_line, p)

        # Split requirements into chunks of up to 7 tags per numeric step
        reqs = hdr.requirements or []
        # Always create at least one substep
        chunks: List[List[str]] = [reqs[i : i + 7] for i in range(0, len(reqs), 7)] or [[]]

        substeps = []
        for idx, chunk in enumerate(chunks, start=1):
            idn = f"{counter:04d}"
            counter += 1

            # Build tests line for this chunk
            if chunk:
                per_file_tests = format_tests_value(chunk, delimiter=" ", max_width=120, indent_spaces=14)
                tests_line = f"      :tests: {per_file_tests}"
            else:
                # No requirements present; fall back to warning + TODO like original behavior
                tests_line = build_tests_line(p, hdr)

            # Only first numeric step contains Input/Output blocks. Others repeat Description only.
            if idx == 1:
                desc_lines = desc_lines_full
                input_lines = input_lines_full
                output_lines = output_lines_full
            else:
                desc_lines = desc_lines_full
                input_lines = []
                output_lines = []

            substeps.append(
                {
                    "index": idx,
                    "id": idn,
                    "tests_line": tests_line,
                    "desc_lines": desc_lines,
                    "input_lines": input_lines,
                    "output_lines": output_lines,
                }
            )

        steps.append(
            {
                "file_display_name": file_display_name,
                "id1": id1,
                "substeps": substeps,
            }
        )

    title = f"{group_conv} Test Specification - oAW tests"
    section = f"{component}_oAW_{group_conv}_Tests"

    if Environment is not None:
        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=False,
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
        )
        template = env.get_template("oaw_test_group.rst.j2")
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
    else:
        # Fallback renderer without Jinja2
        lines: List[str] = []
        lines.append(title)
        lines.append("=" * max(len(title), 120))
        lines.append("")
        lines.append(section)
        lines.append("-" * len(section))
        lines.append("")
        lines.append(f".. sw_test:: {section}")
        lines.append(f"   :id: TS_{section}")
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
        for step in steps:
            lines.append(f"   .. sw_test_step:: {step['file_display_name']}")
            lines.append(f"      :id: TSS_{section}_{step['id1']}")
            lines.append("      :collapse: true")
            lines.append("")
            for sub in step["substeps"]:
                lines.append(f"   .. sw_test_step:: {sub['index']}")
                lines.append(f"      :id: TSS_{section}_{sub['id']}")
                lines.append("      :collapse: true")
                lines.append(sub["tests_line"])
                lines.append("")
                # Description (always present)
                lines.extend(sub["desc_lines"])
                lines.append("")
                if sub["input_lines"]:
                    lines.extend(sub["input_lines"])
                    lines.append("")
                    lines.extend(sub["output_lines"])
                # If no input/output lines for this substep, do not add extra trailing blank lines
        lines.append("")
        content = "\n".join(lines)

    try:
        out_path.write_text(content, encoding="utf-8")
        print(f"{out_path}")
    except Exception as ex:
        report_error(out_path, 1, f"Failed to write group RST: {ex}")
    return out_path
