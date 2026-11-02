"""Platform dialog adapters preserve paths and close their GUI resources."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from ne111_checker import native_file_dialog


@pytest.mark.parametrize("filename", ("/tmp/Student's work/Café.py", ""))
def test_macos_dialog_passes_paths_as_arguments(monkeypatch, filename):
    monkeypatch.setattr(native_file_dialog.sys, "platform", "darwin")
    run = Mock(return_value=SimpleNamespace(stdout=filename + "\n"))
    monkeypatch.setattr(native_file_dialog.subprocess, "run", run)

    assert native_file_dialog.choose_file("/tmp/Student's work", "A6.py") == filename

    command = run.call_args.args[0]
    assert command[0] == "/usr/bin/osascript"
    assert command[-3:] == ["--", "/tmp/Student's work", "py"]
    assert run.call_args.kwargs["check"]


@pytest.mark.parametrize("fails", (False, True))
def test_tk_dialog_uses_native_picker_and_closes_root(monkeypatch, tmp_path, fails):
    monkeypatch.setattr(native_file_dialog.sys, "platform", "win32")
    monkeypatch.setattr(native_file_dialog.sys, "base_prefix", str(tmp_path))
    for library, filename in (("tcl8.6", "init.tcl"), ("tk8.6", "tk.tcl")):
        directory = tmp_path / "tcl" / library
        directory.mkdir(parents=True)
        (directory / filename).touch()
    monkeypatch.delenv("TCL_LIBRARY", raising=False)
    monkeypatch.delenv("TK_LIBRARY", raising=False)
    root = Mock()
    ask = Mock(return_value="C:/Saved assignments/A1.ipynb")
    if fails:
        ask.side_effect = RuntimeError("Dialog failed")
    monkeypatch.setitem(
        sys.modules, "_tkinter", SimpleNamespace(TCL_VERSION="8.6", TK_VERSION="8.6")
    )
    monkeypatch.setitem(
        sys.modules,
        "tkinter",
        SimpleNamespace(
            Tk=lambda: root, filedialog=SimpleNamespace(askopenfilename=ask)
        ),
    )

    if fails:
        with pytest.raises(RuntimeError, match="Dialog failed"):
            native_file_dialog.choose_file("C:/Saved assignments", "A1.ipynb")
    else:
        assert (
            native_file_dialog.choose_file("C:/Saved assignments", "A1.ipynb")
            == "C:/Saved assignments/A1.ipynb"
        )

    assert ask.call_args.kwargs["initialdir"] == "C:/Saved assignments"
    assert ask.call_args.kwargs["filetypes"] == [
        ("Assignment files (.ipynb)", "*.ipynb")
    ]
    root.destroy.assert_called_once()
    assert native_file_dialog.os.environ["TCL_LIBRARY"] == str(tmp_path / "tcl/tcl8.6")
