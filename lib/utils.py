from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# ANSI colors
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RESET = "\033[0m"

# Global flags
HAS_WARNINGS: bool = False
HAS_ERRORS: bool = False


def _print_banner(text: str, color: str) -> None:
    print(f"{color}{text}{RESET}")


def print_final_status_banner() -> None:
    global HAS_WARNINGS, HAS_ERRORS
    if HAS_ERRORS:
        _print_banner(
            "/-------------------\\\n| OAW TO RST FAILED |\n\\-------------------/",
            RED,
        )
    elif HAS_WARNINGS:
        _print_banner(
            "/-----------------------------------\\\n| OAW TO RST FINISHED WITH WARNINGS |\n\\-----------------------------------/",
            YELLOW,
        )
    else:
        _print_banner(
            "/---------------------------\\\n| OAW TO RST WAS SUCCESSFUL |\n\\---------------------------/",
            GREEN,
        )


def report_error(file: Path, line: int, code: int, message: str) -> None:
    global HAS_ERRORS
    HAS_ERRORS = True
    print(f"{file}:{line}: (ERROR) {message}", file=sys.stderr)
    # Print banner at the end before exiting
    print_final_status_banner()
    sys.exit(1)


def collect_error(file: Path, line: int, code: int, message: str) -> None:
    """Record a non-fatal error and continue execution.

    Used for aggregating errors across multiple .tsc files so developers can
    see all issues in one run. This function does NOT exit the process.
    """
    global HAS_ERRORS
    HAS_ERRORS = True
    print(f"{file}:{line}: (ERROR) {message}", file=sys.stderr)


def has_errors() -> bool:
    return HAS_ERRORS


def report_warning(file: Path, line: int, code: int, message: str) -> None:
    global HAS_WARNINGS
    HAS_WARNINGS = True
    print(f"{file}:{line}: (WARNING) {message}", file=sys.stderr)


def ensure_jinja2_installed() -> None:
    try:
        import jinja2  # noqa: F401
        return
    except Exception:
        # Attempt user-site install first; if blocked by PEP 668, override safely
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--user", "Jinja2>=3.1,<4"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--break-system-packages",
                    "--user",
                    "Jinja2>=3.1,<4",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
