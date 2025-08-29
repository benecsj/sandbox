from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from .config_handler import Config
from .utils import report_error, collect_error


def validate_paths(config: Config) -> None:
    if not config.test_path.exists() or not config.test_path.is_dir():
        report_error(config.test_path, 1, 1101, "'test_path' does not exist or is not a directory")
    if not config.spec_path.exists() or not config.spec_path.is_dir():
        report_error(config.spec_path, 1, 1102, "'spec_path' does not exist or is not a directory")


def discover_tsc_files(config: Config) -> List[Path]:
    prefix = f"{config.component}_"
    results: List[Path] = []
    print("Test (.tsc) files found:")
    for path in config.test_path.rglob("*.tsc"):
        if path.name.startswith(prefix):
            results.append(path.resolve())
    results.sort(key=lambda p: str(p))
    for p in results:
        print(str(p))
    if not results:
        print(f"No oAW tests found for {config.component}.")
    print("")
    return results


def group_tsc_files_by_group(component: str, tsc_files: List[Path]) -> Dict[str, List[Path]]:
    groups: Dict[str, List[Path]] = {}
    for file_path in tsc_files:
        stem = file_path.stem
        parts = stem.split("_")
        if len(parts) < 3 or parts[0] != component:
            collect_error(file_path, 1, 1201, "No valid group token in filename")
            continue
        group = parts[1]
        groups.setdefault(group, []).append(file_path)
    for group_name in groups:
        groups[group_name].sort(key=lambda p: str(p))
    return dict(sorted(groups.items(), key=lambda kv: kv[0]))


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


def parse_tsc_header(path: Path) -> TscHeader | None:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as ex:
        collect_error(path, 1, 1401, f"Failed to read .tsc file: {ex}")
        return None

    lines = text.splitlines()
    idx = 0

    def strip_comment_prefix(s: str) -> str:
        if not s.lstrip().startswith("//"):
            return s
        s2 = s.lstrip()[2:]
        if s2.startswith(" "):
            s2 = s2[1:]
        return s2

    sections = {"description": [], "input": [], "output": [], "requirements": []}
    current: str | None = None
    expected_order = ["description", "input", "output", "requirements"]
    order_index = 0
    seen_tokens: set[str] = set()
    header_lines: Dict[str, int] = {}

    while idx < len(lines):
        raw = lines[idx]
        if not raw.strip():
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
                    collect_error(path, idx + 1, 1402, f"Unexpected or out-of-order section '{name}'")
                    return None
                current = name
                order_index += 1
                seen_tokens.add(name)
                header_lines[name] = idx + 1
            else:
                if current is None:
                    collect_error(path, idx + 1, 1403, "Header must start with 'Description'")
                    return None
                sections[current].append(content.rstrip())
            idx += 1
            continue
        else:
            if order_index == 0:
                collect_error(path, 1, 1404, "Header missing")
                return None
            break

    missing_tokens = [tok for tok in expected_order if tok not in seen_tokens]
    if missing_tokens:
        collect_error(path, 1, 1405, f"Missing header section(s): {', '.join(t.capitalize() for t in missing_tokens)}")
        return None

    all_present_empty = all(len(sections[key]) == 0 for key in expected_order)

    req_line = " ".join(sections["requirements"]).replace(",", " ")
    tags_raw = [t.strip() for t in req_line.split() if t.strip()]
    tags = sorted(set(tags_raw))

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


def parse_all_headers(tsc_file_groups: Dict[str, List[Path]]) -> Dict[str, List[Tuple[Path, TscHeader]]]:
    parsed_groups: Dict[str, List[Tuple[Path, TscHeader]]] = {}
    for group, files in tsc_file_groups.items():
        parsed_list: List[Tuple[Path, TscHeader]] = []
        for p in files:
            hdr = parse_tsc_header(p)
            if hdr is None:
                # Skip invalid file; error already collected
                continue
            parsed_list.append((p, hdr))
        parsed_groups[group] = parsed_list
    return parsed_groups
