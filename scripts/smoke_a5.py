"""Exercise an installed A5 checker through its CLI and Streamlit interface."""

from __future__ import annotations

import importlib.util
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from streamlit.testing.v1 import AppTest


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="ne111-a5-smoke-") as temporary:
        directory = Path(temporary)
        submission = directory / "A5.ipynb"
        submission.write_text(
            json.dumps(
                {
                    "nbformat": 4,
                    "nbformat_minor": 5,
                    "metadata": {},
                    "cells": [
                        {
                            "cell_type": "code",
                            "metadata": {},
                            "source": (
                                "# A5Q3\n"
                                "with open(filename, 'w') as file:\n"
                                "    file.write((value + '\\n') * repetitions)\n"
                                "answer = None"
                            ),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]

        with (directory / "streamlit.log").open("w+") as log:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "ne111_checker",
                    "A5",
                    "--headless",
                    "--port",
                    str(port),
                ],
                cwd=directory,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=os.name != "nt",
            )
            try:
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    try:
                        with urllib.request.urlopen(
                            f"http://127.0.0.1:{port}/_stcore/health", timeout=1
                        ) as response:
                            if response.status == 200:
                                break
                    except (urllib.error.URLError, TimeoutError):
                        pass
                    if process.poll() is not None:
                        raise AssertionError("The checker exited during startup")
                    time.sleep(0.25)
                else:
                    raise AssertionError("The checker did not become healthy")

                os.environ["NE111_GRADER_ASSIGNMENT"] = "A5"
                os.environ["NE111_GRADER_SUBMISSION"] = str(submission)
                spec = importlib.util.find_spec("ne111_checker.student_app")
                assert spec is not None and spec.origin is not None
                app = AppTest.from_file(Path(spec.origin)).run(timeout=20)
                app.button[2].click().run(timeout=20)
                assert not app.exception
                assert not app.error
                assert len(app.success) == 2
                print(
                    "Installed A5 CLI is healthy; Q3 writes the expected file from A5.ipynb."
                )
            except BaseException:
                log.seek(0)
                print(log.read(), file=sys.stderr)
                raise
            finally:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        capture_output=True,
                        check=False,
                    )
                else:
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


if __name__ == "__main__":
    main()
