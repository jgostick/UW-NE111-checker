"""Exercise real Linux file selection and cancellation under xvfb-run."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def main() -> None:
    # Keep GTK on the test X display, even when the host uses Wayland.
    environment = os.environ | {"GDK_BACKEND": "x11", "GTK_USE_PORTAL": "0"}
    with tempfile.TemporaryDirectory(prefix="ne111-dialog-smoke-") as temporary:
        directory = Path(temporary) / "Saved assignments"
        directory.mkdir()
        submission = directory / "A6.py"
        submission.write_text("# Synthetic dialog test file\n", encoding="utf-8")
        for cancelled in (False, True):
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-c",
                    (
                        "import runpy, sys; "
                        "sys.modules['_tkinter'] = None; "
                        "sys.modules['tkinter'] = None; "
                        "runpy.run_module('ne111_checker.native_file_dialog', "
                        "run_name='__main__')"
                    ),
                    str(directory),
                    submission.name,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=environment,
                start_new_session=True,
            )
            try:
                window = subprocess.run(
                    [
                        "xdotool",
                        "search",
                        "--sync",
                        "--onlyvisible",
                        "--name",
                        "^Choose your assignment file$",
                    ],
                    capture_output=True,
                    text=True,
                    env=environment,
                    check=True,
                    timeout=15,
                ).stdout.splitlines()[-1]

                def control(*arguments: str) -> None:
                    subprocess.run(
                        ["xdotool", *arguments],
                        env=environment,
                        check=True,
                        timeout=5,
                    )

                control("windowfocus", "--sync", window)
                time.sleep(0.5)  # Let GTK finish loading and focus the dialog.
                if cancelled:
                    control("key", "--clearmodifiers", "Escape")
                else:
                    control("key", "--clearmodifiers", "ctrl+l")
                    time.sleep(0.2)
                    control("type", "--clearmodifiers", "--delay", "1", str(submission))
                    control("key", "--clearmodifiers", "Return")
                    # GTK may first resolve the typed path before accepting it.
                    time.sleep(0.5)
                    if process.poll() is None:
                        control("key", "--clearmodifiers", "Return")
                stdout, stderr = process.communicate(timeout=15)
                assert process.returncode == 0, stderr
                assert json.loads(stdout) == ("" if cancelled else str(submission))
            finally:
                # A failure must also close the dialog child, not just Python.
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                process.wait(timeout=5)
    print("Linux native file selection and cancellation passed.")


if __name__ == "__main__":
    main()
