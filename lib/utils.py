"""Utility helpers for status banners and dependency management."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RESET = "\033[0m"

# Global flags
HAS_WARNINGS: bool = False
HAS_ERRORS: bool = False

EXIT_FAILURE = 1


def _print_banner(text: str, color: str) -> None:
    """Render a colored banner to stdout."""
    print(f"{color}{text}{RESET}")


def print_final_status_banner() -> None:
    """Display a summary banner reflecting overall script status."""
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


def print_skipped_banner() -> None:
    """Display a yellow banner indicating the run was skipped."""
    _print_banner(
        "/--------------------\\\n| OAW TO RST SKIPPED |\n\\--------------------/",
        YELLOW,
    )


def report_error(file: Path, line: int, message: str) -> None:
    """Log a fatal error, show the final banner, and exit."""
    global HAS_ERRORS
    HAS_ERRORS = True
    print(f"{file}:{line}: (ERROR) {message}", file=sys.stderr)
    # Print banner at the end before exiting
    print_final_status_banner()
    sys.exit(EXIT_FAILURE)


def collect_error(file: Path, line: int, message: str) -> None:
    """Record a non-fatal error and continue execution.

    Used for aggregating errors across multiple .tsc files so developers can
    see all issues in one run. This function does NOT exit the process.
    """
    global HAS_ERRORS
    HAS_ERRORS = True
    print(f"{file}:{line}: (ERROR) {message}", file=sys.stderr)


def has_errors() -> bool:
    """Return True if any errors have been recorded."""
    return HAS_ERRORS


def report_warning(file: Path, line: int, message: str) -> None:
    """Log a warning without halting execution."""
    global HAS_WARNINGS
    HAS_WARNINGS = True
    print(f"{file}:{line}: (WARNING) {message}", file=sys.stderr)


def ensure_jinja2_installed() -> None:
    """Ensure ``Jinja2`` is importable in the current process.

    Performs a best-effort runtime installation to user site and updates
    ``sys.path`` so the current interpreter can import it without restart.
    """
    try:
        import jinja2  # noqa: F401
        return
    except Exception:
        pass

    # Attempt installation
    install_cmds = [
        [sys.executable, "-m", "pip", "install", "--user", "Jinja2>=3.1,<4"],
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--break-system-packages",
            "--user",
            "Jinja2>=3.1,<4",
        ],
    ]
    for cmd in install_cmds:
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            break
        except Exception:
            continue

    # Ensure user site and site-packages are on sys.path for this process
    try:
        import site  # noqa: F401
        user_site_paths = []
        try:
            # Python 3.10+: returns str or list[str] depending on env
            usp = site.getusersitepackages()
            if isinstance(usp, str):
                user_site_paths.append(usp)
            elif isinstance(usp, list):
                user_site_paths.extend(usp)
        except Exception:
            user_site_paths = []

        # Add discovered site paths to sys.path if missing
        for p in user_site_paths:
            if p and p not in sys.path:
                sys.path.append(p)
    except Exception:
        pass

    # Invalidate import caches and try again
    try:
        import importlib

        importlib.invalidate_caches()
        import jinja2  # noqa: F401
    except Exception:
        # As a last resort, let the import fail naturally later
        pass
