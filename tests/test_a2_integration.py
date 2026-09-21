"""Integration coverage for the notebook-based Assignment 2."""

from __future__ import annotations

import json

from ne111_checker.isolated import run_question_isolated
from ne111_checker.registry import assignment_ids, get_assignment


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
    "# A2Q1\nanswer = float(a)",
    "# A2Q2\nanswer = int(float(a))",
    "# A2Q3\nanswer = a % b",
    "# A2Q4\nanswer = (int(a), a % 1)",
    "# A2Q5\nanswer = str(type(a))",
    "# A2Q6\nanswer = a + b",
    "# A2Q7\na[key] = val\nanswer = a",
    "# A2Q8\na.remove(val)\nanswer = a",
    "# A2Q9\nanswer = a[:len(a) // 2]",
    "# A2Q10\nanswer = max(a) - min(a)",
]


def test_public_a2_reference_notebook_passes(tmp_path) -> None:
    submission = tmp_path / "A2.ipynb"
    submission.write_bytes(_notebook(REFERENCE_CELLS))
    assignment = get_assignment("A2")

    results = tuple(
        run_question_isolated("A2", question.id, submission)
        for question in assignment.questions
    )

    assert all(result.passed for result in results)
    assert sum(len(result.cases) for result in results) == 29
    assert assignment_ids() == tuple(f"A{number}" for number in range(1, 10))
