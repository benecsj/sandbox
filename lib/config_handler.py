from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Dict
from pathlib import Path

from .utils import report_error


@dataclass
class Config:
    component: str
    test_path: Path
    spec_path: Path
    group_name_mappings: Dict[str, str]


def load_config_with_overrides(script_path: Path) -> Config:
    parser = argparse.ArgumentParser(description="oAW to RST generator")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to config JSON (absolute or relative to script)",
        default=None,
    )
    parser.add_argument("--component", type=str, help="Component name", default=None)
    parser.add_argument("--test_path", type=str, help="Path to test files", default=None)
    parser.add_argument("--spec_path", type=str, help="Path to spec files", default=None)
    args = parser.parse_args()

    # Determine config.json location (default in ./config/config.json next to script)
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
        script_dir = script_path.parent
        config_dir = script_dir / "config"
        config_path = config_dir / "config.json"
        if not config_path.exists():
            report_error(
                config_path, 1, 1001, "config.json not found in ./config next to oaw_to_rst.py"
            )

    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    component = args.component or raw.get("component")
    test_path_raw = args.test_path or raw.get("test_path")
    spec_path_raw = args.spec_path or raw.get("spec_path")
    group_name_mappings_raw = raw.get("group_name_mappings")

    if not component or not isinstance(component, str):
        report_error(config_path, 1, 1002, "Invalid or missing 'component' in configuration")

    if not test_path_raw or not isinstance(test_path_raw, str):
        report_error(config_path, 1, 1003, "Invalid or missing 'test_path' in configuration")

    if not spec_path_raw or not isinstance(spec_path_raw, str):
        report_error(config_path, 1, 1004, "Invalid or missing 'spec_path' in configuration")

    # group_name_mappings is mandatory and not overrideable via CLI
    if not isinstance(group_name_mappings_raw, dict) or not group_name_mappings_raw:
        report_error(config_path, 1, 1005, "Invalid or missing 'group_name_mappings' in configuration")
    # Normalize keys to lowercase and ensure values are strings
    group_name_mappings: Dict[str, str] = {}
    for k, v in group_name_mappings_raw.items():
        if not isinstance(k, str) or not isinstance(v, str) or not k.strip():
            report_error(config_path, 1, 1006, "'group_name_mappings' must map non-empty strings to strings")
        group_name_mappings[k.strip().lower()] = v.strip()

    test_path = Path(test_path_raw)
    spec_path = Path(spec_path_raw)

    if not test_path.is_absolute():
        test_path = (config_dir / test_path).resolve()
    if not spec_path.is_absolute():
        spec_path = (config_dir / spec_path).resolve()

    print(f"Component: {component}")
    print(f"Test path: {test_path}")
    print(f"Spec path: {spec_path}")
    print("")
    return Config(component=component, test_path=test_path, spec_path=spec_path, group_name_mappings=group_name_mappings)
