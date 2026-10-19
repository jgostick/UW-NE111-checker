"""Exercise A5 tagged cells, supplied files, and file-writing side effects."""

from __future__ import annotations

import importlib.util
import json
from dataclasses import replace
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ne111_checker.isolated import run_question_isolated, run_question_source
from ne111_checker.registry import get_assignment
from ne111_checker.worker import run_question_for_assignment

CELLS = [
    "# setup\nimport pandas as pd",
    "# A5Q1\nwith open(filename) as file:\n    answer = len(file.readlines())",
    "# A5Q2\nwith open(filename) as file:\n    answer = len(file.read().split())",
    (
        "# A5Q3\nfilename = 'my_test.txt'\nvalue = 'test'\nrepetitions = 1\n"
        "with open(filename, 'w') as file:\n"
        "    for _ in range(repetitions):\n        file.write(value + '\\n')\n"
        "answer = None"
    ),
    (
        "# A5Q4\nif not filename.endswith('.csv'):\n    filename += '.csv'\n"
        "pd.DataFrame(data).to_csv(filename, index=False)\nanswer = None"
    ),
    (
        "# A5Q5\nif not filename.endswith('.csv'):\n    filename += '.csv'\n"
        "answer = pd.read_csv(filename).to_dict(orient='list')"
    ),
    (
        "# A5Q6\nwith open(filename, 'a') as file:\n"
        "    file.write('\\n' + value)\nanswer = None"
    ),
]


def notebook(cells: list[str]) -> bytes:
    return json.dumps(
        {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {},
            "cells": [
                {"cell_type": "code", "metadata": {}, "source": source}
                for source in cells
            ],
        }
    ).encode()


def test_a5_notebook_passes_without_touching_neighbouring_files(tmp_path) -> None:
    submission = tmp_path / "A5.ipynb"
    submission.write_bytes(notebook(CELLS))
    (tmp_path / "file.txt").write_text("keep this unchanged")
    (tmp_path / "data.csv").write_text("also unchanged")
    assignment = get_assignment("A5")

    assert assignment.notebook_submission
    assert assignment.expected_filename == "A5.ipynb"
    # Reading after Q6 also verifies that its append does not leak into Q1/Q2.
    for question in reversed(assignment.questions):
        result = run_question_isolated("A5", question.id, submission)
        assert result.passed, result.to_dict()
        assert len(result.cases) == len(question.cases)

    assert (tmp_path / "file.txt").read_text() == "keep this unchanged"
    assert (tmp_path / "data.csv").read_text() == "also unchanged"
    assert not (tmp_path / "output.txt").exists()
    assert not (tmp_path / "output.csv").exists()


@pytest.mark.parametrize(
    ("question_id", "source", "message"),
    (
        ("Q1", "# A5Q2\nanswer = 6", "No code cell is tagged # A5Q1"),
        ("Q1", "# A5Q1\nprint(6)", "did not assign a value to answer"),
        ("Q3", "# A5Q3\nanswer = None", "Could not read output.txt"),
        ("Q4", "# A5Q4\nanswer = None", "Could not read output.csv"),
        ("Q6", "# A5Q6\nanswer = None", "new line"),
    ),
)
def test_a5_reports_incomplete_notebooks(question_id, source, message) -> None:
    result = run_question_source(
        "A5", question_id, notebook([source]), filename="A5.ipynb"
    )

    assert not result.passed
    assert any(
        message in check.message for case in result.cases for check in case.checks
    )


def test_a5_student_app_uses_notebook_inputs_and_checks_file_writes(
    monkeypatch, tmp_path
) -> None:
    (tmp_path / "A5.ipynb").write_bytes(notebook(CELLS))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NE111_GRADER_ASSIGNMENT", "A5")
    monkeypatch.delenv("NE111_GRADER_SUBMISSION", raising=False)
    spec = importlib.util.find_spec("ne111_checker.student_app")
    assert spec is not None and spec.origin is not None

    app = AppTest.from_file(Path(spec.origin)).run(timeout=20)
    assert app.button[3].label == "Run A5Q4 cell"
    assert any(
        'filename = "' in code.value or "filename = '" in code.value
        for code in app.code
    )
    app.button[3].click().run(timeout=20)

    assert not app.exception
    assert not app.error
    assert len(app.tabs) == 6
    assert len(app.success) == 2


@pytest.mark.parametrize(
    ("question_id", "filename"), (("Q4", "output"), ("Q5", "data.csv"))
)
def test_a5_csv_cells_handle_alternate_filename_form(
    question_id, filename, tmp_path
) -> None:
    submission = tmp_path / "A5.ipynb"
    submission.write_bytes(notebook(CELLS))
    assignment = get_assignment("A5")
    question = assignment.question(question_id)
    original = question.cases[0]
    case = replace(original, args=(filename, *original.args[1:]))
    assignment = replace(assignment, questions=(replace(question, cases=(case,)),))

    result = run_question_for_assignment(assignment, question_id, submission)

    assert result.passed, result.to_dict()
