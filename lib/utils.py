from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def report_error(file: Path, line: int, code: int, message: str) -> None:
    print(f"{file}:{line}: (ERROR) {message}", file=sys.stderr)
    sys.exit(1)


def report_warning(file: Path, line: int, code: int, message: str) -> None:
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

