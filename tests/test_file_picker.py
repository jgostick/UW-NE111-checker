"""Selecting a path must preserve live reads across edits and file switches."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from ne111_checker.file_picker import open_file_dialog


def _notebook(answer: str) -> str:
    return json.dumps(
        {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [
                {
                    "cell_type": "code",
                    "metadata": {},
                    "source": f"# A1Q1\nanswer = {answer}",
                }
            ],
        }
    )


_FUNCTION = '''def A6Q6(a, b, c=0):
    """Compute a length.

    Parameters
    ----------
    a, b, c : float
        The components.

    Returns
    -------
    float
        The length.
    """
    return (a**2 + b**2 + c**2)**0.5
'''


@pytest.mark.parametrize(
    ("assignment", "question", "filename", "correct", "incorrect"),
    (
        ("A1", "Q1", "A1.ipynb", _notebook("a % b"), _notebook("None")),
        (
            "A6",
            "Q6",
            "A6.py",
            _FUNCTION,
            _FUNCTION.replace("return (a**2 + b**2 + c**2)**0.5", "return None"),
        ),
    ),
)
def test_selected_file_outside_launch_folder_is_reread(
    monkeypatch, tmp_path, assignment, question, filename, correct, incorrect
) -> None:
    launch = tmp_path / "Launch folder"
    launch.mkdir()
    work = tmp_path / "Saved assignments"
    work.mkdir()
    submission = work / filename
    submission.write_text(correct)
    monkeypatch.chdir(launch)
    monkeypatch.setenv("NE111_GRADER_ASSIGNMENT", assignment)
    monkeypatch.delenv("NE111_GRADER_SUBMISSION", raising=False)
    spec = importlib.util.find_spec("ne111_checker.student_app")
    assert spec is not None and spec.origin is not None
    app = AppTest.from_file(spec.origin).run(timeout=20)
    assert app.button(key=f"run-{question}").disabled

    dialog = Mock(return_value=submission)
    monkeypatch.setattr("ne111_checker.file_picker.open_file_dialog", dialog)
    app.button(key="browse-submission").click().run(timeout=20)
    assert dialog.call_args.args == (launch, filename)
    app.button(key=f"run-{question}").click().run(timeout=20)
    assert not app.exception
    assert not app.error
    assert app.success

    submission.write_text(incorrect)
    app.run(timeout=20)
    assert not app.success  # Previous feedback is invalidated after a saved edit.
    app.button(key=f"run-{question}").click().run(timeout=20)
    assert not app.exception
    assert app.error

    other = work / f"other-{filename}"
    other.write_text(correct)
    dialog.return_value = other
    app.button(key="browse-submission").click().run(timeout=20)
    assert not app.error
    app.button(key=f"run-{question}").click().run(timeout=20)
    assert not app.exception
    assert not app.error
    assert app.success

    other.unlink()
    app.run(timeout=20)
    assert not app.exception
    assert app.button(key=f"run-{question}").disabled
    assert not app.success


@pytest.mark.parametrize("cancelled", (True, False))
def test_cancel_or_failure_preserves_selected_file(monkeypatch, tmp_path, cancelled):
    submission = tmp_path / "A6.py"
    submission.write_text(_FUNCTION)
    monkeypatch.setenv("NE111_GRADER_ASSIGNMENT", "A6")
    monkeypatch.setenv("NE111_GRADER_SUBMISSION", str(submission))
    dialog = (
        Mock(return_value=None)
        if cancelled
        else Mock(side_effect=RuntimeError("Unavailable"))
    )
    monkeypatch.setattr("ne111_checker.file_picker.open_file_dialog", dialog)
    spec = importlib.util.find_spec("ne111_checker.student_app")
    app = AppTest.from_file(spec.origin).run(timeout=20)
    app.button(key="browse-submission").click().run(timeout=20)
    assert not app.exception
    assert not app.button(key="run-Q6").disabled
    assert bool(app.warning) is not cancelled
    if not cancelled:
        alternate = tmp_path / "other.py"
        alternate.write_text(_FUNCTION)
        app.text_input[0].set_value(str(alternate))
        next(button for button in app.button if button.label == "Use file").click().run(
            timeout=20
        )
        assert app.session_state["checker-submission"] == str(alternate)


def test_native_dialog_runs_in_a_separate_python_process(monkeypatch, tmp_path):
    submission = tmp_path / "Assignment with spaces.py"
    submission.touch()
    run = Mock(return_value=SimpleNamespace(stdout=json.dumps(str(submission))))
    monkeypatch.setattr("ne111_checker.file_picker.subprocess.run", run)
    assert open_file_dialog(tmp_path, "A6.py") == submission
    command = run.call_args.args[0]
    assert command[1:] == [
        "-m",
        "ne111_checker.native_file_dialog",
        str(tmp_path),
        "A6.py",
    ]
    assert run.call_args.kwargs["check"]


@pytest.mark.parametrize("result", ('""', "null"))
def test_native_dialog_cancellation(monkeypatch, tmp_path, result):
    monkeypatch.setattr(
        "ne111_checker.file_picker.subprocess.run",
        Mock(return_value=SimpleNamespace(stdout=result)),
    )
    assert open_file_dialog(tmp_path, "A6.py") is None


@pytest.mark.parametrize(
    "failure", (OSError("missing Python"), subprocess.CalledProcessError(1, ["python"]))
)
def test_native_dialog_errors_are_reported(monkeypatch, tmp_path, failure):
    monkeypatch.setattr(
        "ne111_checker.file_picker.subprocess.run", Mock(side_effect=failure)
    )
    with pytest.raises(RuntimeError, match="could not be opened"):
        open_file_dialog(tmp_path, "A6.py")


def test_native_dialog_filters_file_type(monkeypatch, tmp_path):
    notebook = tmp_path / "A1.ipynb"
    notebook.touch()
    monkeypatch.setattr(
        "ne111_checker.file_picker.subprocess.run",
        Mock(return_value=SimpleNamespace(stdout=json.dumps(str(notebook)))),
    )
    with pytest.raises(RuntimeError, match="existing .py file"):
        open_file_dialog(tmp_path, "A6.py")
