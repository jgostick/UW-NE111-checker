"""Select a local submission with the system file dialog and retain its path."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import streamlit as st


def open_file_dialog(initial_directory: Path, expected_name: str) -> Path | None:
    """Run the GUI on a child process's main thread, including on macOS."""
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ne111_checker.native_file_dialog",
                str(initial_directory),
                expected_name,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        filename = json.loads(result.stdout)
        if filename is not None and not isinstance(filename, str):
            raise TypeError("The system file dialog returned an invalid path.")
    except (OSError, subprocess.CalledProcessError, ValueError, TypeError) as error:
        raise RuntimeError("The system file dialog could not be opened.") from error
    if not filename:
        return None
    path = Path(filename).resolve()
    if not path.is_file() or path.suffix.lower() != Path(expected_name).suffix.lower():
        raise RuntimeError(f"Choose an existing {Path(expected_name).suffix} file.")
    return path


def submission_picker(default: Path, expected_name: str) -> Path:
    """Render Browse and return the selected path, or the CLI/default path."""
    selected = Path(st.session_state.get("checker-submission", str(default)))
    if st.button("Browse…", key="browse-submission"):
        directory = selected.parent if selected.parent.is_dir() else Path.home()
        try:
            with st.spinner("Choose a file in the system file dialog…"):
                chosen = open_file_dialog(directory, expected_name)
            if chosen is not None:
                selected = chosen
                st.session_state["checker-submission"] = str(chosen)
            st.session_state.pop("file-picker-error", None)
        except RuntimeError as error:
            st.session_state["file-picker-error"] = str(error)

    if error := st.session_state.get("file-picker-error"):
        st.warning(f"{error} You can enter the full file path below instead.")
        with st.form("file-picker-path"):
            filename = st.text_input("Assignment file path", value=str(selected))
            if st.form_submit_button("Use file"):
                path = Path(filename.strip().strip('"')).expanduser()
                if path.is_file() and path.suffix.lower() == Path(expected_name).suffix:
                    st.session_state["checker-submission"] = str(path.resolve())
                    st.session_state.pop("file-picker-error", None)
                    st.rerun()
                else:
                    st.error(f"Choose an existing {Path(expected_name).suffix} file.")
    return selected
