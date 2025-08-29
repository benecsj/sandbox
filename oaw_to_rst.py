#!/usr/bin/env python3
"""
oAWToRst (oaw_to_rst.py)

Generates and updates RST documentation for oAW tests based on .tsc files.
Refactored into lib modules and Jinja2 templating.
"""

from __future__ import annotations

import sys
from pathlib import Path

from lib.config_handler import Config, load_config_with_overrides
from lib.file_handler import (
    validate_paths,
    discover_tsc_files,
    group_tsc_files_by_group,
    parse_all_headers,
)
from lib.file_generator import (
    find_toc_rst,
    cleanup_generated_group_files,
    remove_generated_lines_from_toc,
    append_group_links_to_toc,
    generate_group_rst,
)
from lib.utils import print_final_status_banner


def main() -> int:
    print("Running oAW to RST generator")
    print("----------------------------")
    script_path = Path(__file__).resolve()
    config = load_config_with_overrides(script_path)
    validate_paths(config)

    tsc_files = discover_tsc_files(config)
    if not tsc_files:
        return 0

    tsc_file_groups = group_tsc_files_by_group(config.component, tsc_files)
    parsed_groups = parse_all_headers(tsc_file_groups)

    toc_path = find_toc_rst(config.component, config.spec_path)

    cleanup_generated_group_files(config.component, toc_path)
    remove_generated_lines_from_toc(config.component, toc_path)
    append_group_links_to_toc(config.component, list(tsc_file_groups.keys()), toc_path, config.group_name_mappings)

    template_dir = script_path.parent / "config" / "templates"
    toc_dir = toc_path.parent
    print(f"Generated test group rst files:")
    for group_name, parsed_list in parsed_groups.items():
        generate_group_rst(config.component, group_name, parsed_list, toc_dir, template_dir, config.group_name_mappings)

    # Print final banner based on warnings/errors
    print_final_status_banner()
    return 0


if __name__ == "__main__":
    sys.exit(main())
