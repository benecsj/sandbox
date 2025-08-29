from __future__ import annotations

import sys
from pathlib import Path


def report_error(file: Path, line: int, code: int, message: str) -> None:
    print(f"{file}:{line}: (ERROR) {message}", file=sys.stderr)
    sys.exit(1)


def report_warning(file: Path, line: int, code: int, message: str) -> None:
    print(f"{file}:{line}: (WARNING) {message}", file=sys.stderr)

