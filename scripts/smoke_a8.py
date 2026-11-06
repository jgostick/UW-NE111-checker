"""Exercise an installed A8 checker through its CLI and Streamlit interface."""

from __future__ import annotations

import importlib.util
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
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="ne111-a8-smoke-") as temporary:
        directory = Path(temporary)
        submissions = directory / "Saved assignments"
        submissions.mkdir()
        launch = directory / "Launch folder"
        launch.mkdir()
        submission = submissions / "A8.py"
        # This constant answers only the handout example, not arbitrary inputs.
        submission.write_text(
            "def A8Q3(arr):\n    return ((0.2, 0.2), (0.8, 0.7))\n", encoding="utf-8"
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
                    "A8",
                    "--headless",
                    "--port",
                    str(port),
                ],
                cwd=launch,
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

                os.environ["NE111_GRADER_ASSIGNMENT"] = "A8"
                os.environ["NE111_GRADER_SUBMISSION"] = str(launch / "A8.py")
                spec = importlib.util.find_spec("ne111_checker.student_app")
                assert spec is not None and spec.origin is not None
                app = AppTest.from_file(Path(spec.origin)).run(timeout=20)
                assert app.button(key="run-Q3").disabled
                # CI has no interactive desktop; verify the Browse callback
                # using the same path a successful native dialog returns.
                with patch(
                    "ne111_checker.file_picker.open_file_dialog",
                    return_value=submission,
                ):
                    app.button(key="browse-submission").click().run(timeout=20)
                assert not app.exception
                app.button(key="run-Q3").click().run(timeout=20)
                assert not app.exception
                assert not app.error
                assert app.success
                print(
                    "Installed A8 CLI is healthy; Q3 reads the selected external file."
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
