"""Tests for the public tagged-notebook submission convention."""

from __future__ import annotations

import json

from ne111_checker.checks import Equals
from ne111_checker.models import Assignment, Case, Question
from ne111_checker.worker import run_question_for_assignment


def _write_notebook(tmp_path, cells: list[str]):
    notebook = tmp_path / "submission.ipynb"
    notebook.write_text(
        json.dumps(
            {
                "nbformat": 4,
                "nbformat_minor": 5,
                "metadata": {},
                "cells": [
                    {"cell_type": "code", "metadata": {}, "source": source}
                    for source in cells
                ],
            }
        ),
        encoding="utf-8",
    )
    return notebook


def _assignment() -> Assignment:
    return Assignment(
        id="A99",
        title="Notebook test",
        questions=(
            Question(
                id="Q1",
                title="Multiply",
                input_names=("value",),
                cases=(
                    Case("Q1.1", args=(2,), checks=(Equals(6),)),
                    Case("Q1.2", args=(4,), checks=(Equals(12),)),
                ),
            ),
        ),
    )


def test_tagged_answer_cell_is_rerun_with_each_case_input(tmp_path) -> None:
    submission = _write_notebook(
        tmp_path,
        ["# setup\nfactor = 3", "# A99Q1\nanswer = value * factor"],
    )

    result = run_question_for_assignment(_assignment(), "Q1", submission)

    assert [case.passed for case in result.cases] == [True, True]


def test_notebook_cases_have_a_clean_working_directory(tmp_path) -> None:
    submission = _write_notebook(
        tmp_path,
        [
            (
                "# A99Q1\n"
                "from pathlib import Path\n"
                "path = Path('count.txt')\n"
                "count = int(path.read_text()) + 1 if path.exists() else 1\n"
                "path.write_text(str(count))\n"
                "answer = value * count * 3"
            )
        ],
    )

    result = run_question_for_assignment(_assignment(), "Q1", submission)

    assert result.passed


def test_notebook_reports_missing_answer_cell(tmp_path) -> None:
    submission = _write_notebook(tmp_path, ["# A99Q2\nanswer = 1"])

    result = run_question_for_assignment(_assignment(), "Q1", submission)

    assert not result.passed
    assert "No code cell is tagged # A99Q1" in result.cases[0].checks[0].message


def test_notebook_reports_a_cell_without_answer(tmp_path) -> None:
    submission = _write_notebook(tmp_path, ["# A99Q1\nvalue * 3"])

    result = run_question_for_assignment(_assignment(), "Q1", submission)

    assert not result.passed
    assert "did not assign a value to answer" in result.cases[0].checks[0].message


def test_notebook_replaces_student_test_values_with_case_inputs(tmp_path) -> None:
    submission = _write_notebook(
        tmp_path,
        ["# A99Q1\nvalue = 2\nanswer = value * 3"],
    )

    result = run_question_for_assignment(_assignment(), "Q1", submission)

    assert result.passed


def test_notebook_replaces_test_values_after_an_import(tmp_path) -> None:
    submission = _write_notebook(
        tmp_path,
        ["# A99Q1\nimport math\nvalue = 2\nanswer = value * 3"],
    )

    result = run_question_for_assignment(_assignment(), "Q1", submission)

    assert result.passed


def test_notebook_keeps_assignments_after_its_test_values(tmp_path) -> None:
    submission = _write_notebook(
        tmp_path,
        ["# A99Q1\nvalue = 2\nvalue = value * 3\nanswer = value"],
    )

    result = run_question_for_assignment(_assignment(), "Q1", submission)

    assert result.passed
