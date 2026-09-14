"""Command-line launcher for the student Streamlit checker."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from .registry import assignment_ids, get_assignment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ne111-checker")
    parser.add_argument("assignment", choices=assignment_ids(), type=str.upper)
    parser.add_argument(
        "--submission",
        type=Path,
        help="Submission file (defaults to the assignment filename in the current directory)",
    )
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args(argv)

    assignment = get_assignment(args.assignment)
    submission = (
        args.submission or Path.cwd() / assignment.expected_filename
    ).resolve()
    app = Path(__file__).with_name("student_app.py")

    environment = os.environ.copy()
    environment["NE111_GRADER_ASSIGNMENT"] = assignment.id
    environment["NE111_GRADER_SUBMISSION"] = str(submission)

    command = [sys.executable, "-m", "streamlit", "run", str(app)]
    if args.port is not None:
        command.extend(["--server.port", str(args.port)])
    if args.headless:
        command.extend(["--server.headless", "true"])

    try:
        return subprocess.run(command, env=environment, check=False).returncode
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
