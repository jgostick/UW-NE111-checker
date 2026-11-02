"""Main-thread entry point for the operating system's file selection dialog."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def choose_file(initial_directory: str, expected_name: str) -> str:
    if sys.platform == "darwin":
        # Standard Additions supplies the macOS dialog without a GUI toolkit.
        script = """
on run argv
    activate
    try
        set directoryPath to item 1 of argv
        set fileExtension to item 2 of argv
        set chosenFile to choose file with prompt "Choose your assignment file" ¬
            of type {fileExtension} default location (POSIX file directoryPath as alias)
        return POSIX path of chosenFile
    on error errorMessage number errorNumber
        if errorNumber is -128 then return ""
        error errorMessage number errorNumber
    end try
end run
"""
        result = subprocess.run(
            [
                "/usr/bin/osascript",
                "-e",
                script,
                "--",
                initial_directory,
                Path(expected_name).suffix.lstrip("."),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.removesuffix("\n")

    import _tkinter

    # Some standalone Python builds keep these resources under the base
    # installation but search under the virtual environment by default.
    for variable, library, version, filename in (
        ("TCL_LIBRARY", "tcl", _tkinter.TCL_VERSION, "init.tcl"),
        ("TK_LIBRARY", "tk", _tkinter.TK_VERSION, "tk.tcl"),
    ):
        for parent in ("lib", "tcl"):
            directory = Path(sys.base_prefix) / parent / f"{library}{version}"
            if (directory / filename).is_file():
                os.environ.setdefault(variable, str(directory))
                break

    # Import only in the GUI child so a missing Tk installation cannot stop the app.
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
        root.update()
        suffix = Path(expected_name).suffix
        return filedialog.askopenfilename(
            parent=root,
            title="Choose your assignment file",
            initialdir=initial_directory,
            filetypes=[(f"Assignment files ({suffix})", f"*{suffix}")],
        )
    finally:
        root.destroy()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("initial_directory")
    parser.add_argument("expected_name")
    args = parser.parse_args()
    print(json.dumps(choose_file(args.initial_directory, args.expected_name)))


if __name__ == "__main__":
    main()
