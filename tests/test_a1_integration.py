"""Integration coverage for the notebook-based Assignment 1."""

from __future__ import annotations

import json

from ne111_grader.isolated import run_question_isolated, run_question_source
from ne111_grader.registry import get_assignment


def _notebook(cells: list[str]) -> bytes:
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


REFERENCE_CELLS = [
    "# A1Q1\nanswer = a % b",
    "# A1Q2\nanswer = a + b * c",
    "# A1Q3\nx = starting_value\nx = x * scale\nx = x + offset\nanswer = x",
    "# A1Q4\nx, y = starting_x, starting_y\nx, y = y, x\nanswer = x**y",
    "# A1Q5\nanswer = (9 / 5) * celsius + 32",
    "# A1Q6\nimport math\nanswer = math.ceil(value) + math.floor(value) + math.log10(value)",
    "# A1Q7\nanswer = number ** (1 / root)",
    "# A1Q8\nimport math\nanswer = math.pi * radius**2",
    "# A1Q9\nanswer = str(type(value))",
    "# A1Q10\nanswer = abs(a - b)",
]


def test_reference_notebook_passes_all_public_cases(tmp_path) -> None:
    submission = tmp_path / "A1.ipynb"
    submission.write_bytes(_notebook(REFERENCE_CELLS))
    assignment = get_assignment("A1")

    results = [
        run_question_isolated("A1", question.id, submission)
        for question in assignment.questions
    ]

    assert all(result.passed for result in results)


def test_missing_question_cell_is_reported(tmp_path) -> None:
    submission = tmp_path / "A1.ipynb"
    submission.write_bytes(_notebook(["# A1Q2\nanswer = greeting + target"]))

    result = run_question_isolated("A1", "Q1", submission)

    assert not result.passed
    assert "No code cell is tagged # A1Q1" in result.cases[0].checks[0].message


def test_uploaded_notebook_can_have_any_filename() -> None:
    result = run_question_source(
        "A1",
        "Q1",
        _notebook(["# A1Q1\nanswer = a % b"]),
        filename="student_12345_submission.ipynb",
    )

    assert result.passed
