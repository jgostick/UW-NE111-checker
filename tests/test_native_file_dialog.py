"""Platform dialog adapters preserve paths and close their GUI resources."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from ne111_checker import native_file_dialog


@pytest.mark.parametrize(
    ("desktop", "available", "backend"),
    (
        ("ubuntu:GNOME", ("zenity", "kdialog"), "zenity"),
        ("KDE", ("zenity", "kdialog"), "kdialog"),
        ("GNOME", ("kdialog",), "kdialog"),
        ("KDE", ("zenity",), "zenity"),
    ),
)
@pytest.mark.parametrize("cancelled", (False, True))
def test_linux_dialog_works_without_tkinter(
    monkeypatch, desktop, available, backend, cancelled
):
    monkeypatch.setattr(native_file_dialog.sys, "platform", "linux")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", desktop)
    monkeypatch.setattr(
        native_file_dialog.shutil,
        "which",
        lambda name: f"/usr/bin/{name}" if name in available else None,
    )
    monkeypatch.setitem(sys.modules, "_tkinter", None)
    monkeypatch.setitem(sys.modules, "tkinter", None)
    filename = "/tmp/Student's work/Café.py"
    run = Mock(
        return_value=SimpleNamespace(
            returncode=int(cancelled), stdout="" if cancelled else filename + "\n"
        )
    )
    monkeypatch.setattr(native_file_dialog.subprocess, "run", run)

    assert native_file_dialog.choose_file("/tmp/Student's work", "A6.py") == (
        "" if cancelled else filename
    )

    run.assert_called_once()
    command = run.call_args.args[0]
    assert command[0] == f"/usr/bin/{backend}"
    if backend == "zenity":
        assert "--filename=/tmp/Student's work/" in command
        assert "--file-filter=Assignment files (.py) | *.py" in command
    else:
        assert command[-3:] == ["--getopenfilename", "/tmp/Student's work", "*.py"]


@pytest.mark.parametrize("failure", (OSError("Unavailable"), 255))
def test_linux_tries_another_desktop_dialog_on_failure(monkeypatch, failure):
    monkeypatch.setattr(native_file_dialog.sys, "platform", "linux")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME")
    monkeypatch.setattr(native_file_dialog.shutil, "which", lambda name: name)
    run = Mock(
        side_effect=[
            failure
            if isinstance(failure, OSError)
            else SimpleNamespace(returncode=failure, stdout=""),
            SimpleNamespace(returncode=0, stdout="/tmp/A1.ipynb\n"),
        ]
    )
    monkeypatch.setattr(native_file_dialog.subprocess, "run", run)

    assert native_file_dialog.choose_file("/tmp", "A1.ipynb") == "/tmp/A1.ipynb"
    assert [call.args[0][0] for call in run.call_args_list] == ["zenity", "kdialog"]


@pytest.mark.parametrize("available", (False, True))
def test_linux_falls_back_to_tk_if_desktop_tools_are_unavailable(
    monkeypatch, available
):
    monkeypatch.setattr(native_file_dialog.sys, "platform", "linux")
    monkeypatch.setattr(
        native_file_dialog.shutil, "which", lambda name: name if available else None
    )
    monkeypatch.setattr(
        native_file_dialog.subprocess,
        "run",
        Mock(return_value=SimpleNamespace(returncode=255, stdout="")),
    )
    tk = Mock(return_value="/tmp/A6.py")
    monkeypatch.setattr(native_file_dialog, "_choose_tk_file", tk)

    assert native_file_dialog.choose_file("/tmp", "A6.py") == "/tmp/A6.py"
    tk.assert_called_once_with("/tmp", "A6.py")


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
