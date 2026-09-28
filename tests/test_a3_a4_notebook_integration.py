"""Integration coverage for notebook-based Assignments 3 and 4."""

from __future__ import annotations

import json

import pytest

from ne111_checker.isolated import run_question_isolated
from ne111_checker.registry import get_assignment


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


CELLS = {
    "A3": [
        "# A3Q1\nanswer = a < b < c",
        "# A3Q2\nanswer = 0 <= temperature <= 100",
        (
            "# A3Q3\n"
            "if operator == '>':\n    answer = a > b\n"
            "elif operator == '<':\n    answer = a < b\n"
            "elif operator == '==':\n    answer = a == b\n"
            "elif operator == '<=':\n    answer = a <= b\n"
            "elif operator == '>=':\n    answer = a >= b\n"
            "else:\n    answer = a != b"
        ),
        "# A3Q4\nanswer = 0\nfor value in values:\n    if value % 2 == 0:\n        answer += 1",
        "# A3Q5\nanswer = key in dictionary.keys()",
        "# A3Q6\nanswer = type(value) in (int, float, complex)",
        "# A3Q7\nanswer = False\nfor value in values:\n    if type(value) is int:\n        answer = True",
        "# A3Q8\nanswer = True\nfor index in range(len(values) - 1):\n    if values[index] > values[index + 1]:\n        answer = False",
    ],
    "A4": [
        "# A4Q1\nanswer = sum(character.isalpha() for character in value)",
        "# A4Q2\nanswer = len(value.replace(' ', ''))",
        "# A4Q3\nspecial = '!@#$%^&'\nanswer = (any(character.isupper() for character in password) and any(character.islower() for character in password) and any(character.isdigit() for character in password) and any(character in special for character in password))",
        "# A4Q4\nanswer = email.endswith(domain)",
        "# A4Q5\nanswer = [filename for filename in filenames if filename.endswith('.' + extension.removeprefix('.'))]",
        "# A4Q6\nanswer = a < b",
        "# A4Q7\nanswer = ''.join(values)",
        "# A4Q8\nanswer = dict(item.split(':') for item in value.split(';'))",
        (
            "# A4Q9\nimport random\nimport string\n"
            "if mode == 'encrypt':\n    answer = ''.join(character + ''.join(random.choices(string.ascii_letters, k=number)) for character in message)\n"
            "else:\n    answer = message[::number + 1]"
        ),
    ],
}


@pytest.mark.parametrize("assignment_id", tuple(CELLS))
def test_reference_notebook_passes(assignment_id, tmp_path) -> None:
    submission = tmp_path / f"{assignment_id}.ipynb"
    submission.write_bytes(_notebook(CELLS[assignment_id]))
    assignment = get_assignment(assignment_id)

    results = tuple(
        run_question_isolated(assignment_id, question.id, submission)
        for question in assignment.questions
    )

    assert all(result.passed for result in results)
