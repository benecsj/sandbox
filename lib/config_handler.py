from __future__ import annotations

"""Configuration handling for the oAW to RST generator."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from .utils import report_error


# Default location of the configuration file relative to the script.
DEFAULT_CONFIG_RELATIVE_PATH = Path("config/config.json")


@dataclass
class Config:
    """Resolved configuration values for the generator."""

    component: str
    test_path: Path
    spec_path: Path
    group_name_mappings: Dict[str, str]


def _parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the generator."""

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
    return parser.parse_args()


def _resolve_config_path(script_path: Path, config_arg: str | None) -> tuple[Path, Path]:
    """Determine the configuration file path and its directory."""

    script_dir = script_path.parent
    if config_arg:
        specified = Path(config_arg)
        config_path = (
            specified if specified.is_absolute() else (script_dir / specified).resolve()
        )
    else:
        config_path = script_dir / DEFAULT_CONFIG_RELATIVE_PATH
    if not config_path.exists():
        report_error(config_path, 1, f"config file not found: {config_path}")
    return config_path, config_path.parent


def _load_raw_config(config_path: Path) -> Dict[str, object]:
    """Load raw JSON configuration."""

    with config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _normalize_group_mappings(
    config_path: Path, raw_mappings: object
) -> Dict[str, str]:
    """Validate and normalize group name mappings."""

    if not isinstance(raw_mappings, dict) or not raw_mappings:
        report_error(
            config_path,
            1,
            "Invalid or missing 'group_name_mappings' in configuration",
        )
    mappings: Dict[str, str] = {}
    for key, value in raw_mappings.items():
        if not isinstance(key, str) or not isinstance(value, str) or not key.strip():
            report_error(
                config_path,
                1,
                "'group_name_mappings' must map non-empty strings to strings",
            )
        mappings[key.strip().lower()] = value.strip()
    return mappings


def _resolve_path(base_dir: Path, path_str: str) -> Path:
    """Convert ``path_str`` to an absolute :class:`Path` relative to ``base_dir``."""

    path = Path(path_str)
    return path if path.is_absolute() else (base_dir / path).resolve()


def load_config_with_overrides(script_path: Path) -> Config:
    """Load configuration from JSON and apply CLI overrides.

    Parameters
    ----------
    script_path:
        Absolute path to the running script.

    Returns
    -------
    Config
        Configuration object with absolute paths and normalized mappings.
    """

    args = _parse_arguments()
    config_path, config_dir = _resolve_config_path(script_path, args.config)
    raw = _load_raw_config(config_path)

    component = args.component or raw.get("component")
    test_path_raw = args.test_path or raw.get("test_path")
    spec_path_raw = args.spec_path or raw.get("spec_path")
    group_name_mappings_raw = raw.get("group_name_mappings")

    if not component or not isinstance(component, str):
        report_error(
            config_path,
            1,
            "Invalid or missing 'component' in configuration",
        )
    if not test_path_raw or not isinstance(test_path_raw, str):
        report_error(
            config_path,
            1,
            "Invalid or missing 'test_path' in configuration",
        )
    if not spec_path_raw or not isinstance(spec_path_raw, str):
        report_error(
            config_path,
            1,
            "Invalid or missing 'spec_path' in configuration",
        )

    group_name_mappings = _normalize_group_mappings(
        config_path, group_name_mappings_raw
    )

    test_path = _resolve_path(config_dir, test_path_raw)
    spec_path = _resolve_path(config_dir, spec_path_raw)

    print(f"Component: {component}")
    print(f"Test path: {test_path}")
    print(f"Spec path: {spec_path}")
    print("")

    return Config(
        component=component,
        test_path=test_path,
        spec_path=spec_path,
        group_name_mappings=group_name_mappings,
    )

