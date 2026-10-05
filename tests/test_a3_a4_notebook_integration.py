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


@pytest.mark.parametrize(
    ("question_id", "source"),
    (
        ("Q2", "answer = len(''.join(value.split()))"),
        ("Q2", "answer = len(str(value).replace(' ', ''))"),
        *(
            (
                "Q3",
                "answer = "
                + " and ".join(
                    expression
                    for category, expression in (
                        ("upper", "any(c.isupper() for c in password)"),
                        ("lower", "any(c.islower() for c in password)"),
                        ("digit", "any(c.isdigit() for c in password)"),
                        ("special", "any(c in '!@#$%^&' for c in password)"),
                    )
                    if category != missing
                ),
            )
            for missing in ("upper", "lower", "digit", "special")
        ),
        (
            "Q3",
            (
                "answer = any(c.isupper() for c in password) and "
                "any(c.islower() for c in password) and "
                "any(c.isdigit() for c in password) and "
                "any(not c.isalnum() for c in password)"
            ),
        ),
        ("Q4", "answer = domain in email"),
        ("Q4", "answer = email.lower().endswith(domain.lower())"),
        ("Q5", "answer = [name for name in filenames if extension in name]"),
        ("Q5", "answer = [name for name in filenames if name.endswith(extension)]"),
        (
            "Q5",
            (
                "answer = [name for name in filenames "
                "if name.lower().endswith('.' + extension.lower())]"
            ),
        ),
        ("Q6", "answer = a <= b"),
        ("Q6", "answer = int(a < b)"),
        ("Q7", "answer = ' '.join(values)"),
        ("Q7", "answer = ''.join(str(value) for value in values)"),
        ("Q8", "answer = dict(pair.split(':', 1) for pair in value.split(';'))"),
        (
            "Q8",
            (
                "answer = {}\nfor pair in value.split(';'):\n"
                "    key, item = pair.split(':')\n"
                "    answer[key] = int(item) if item.isdigit() else item"
            ),
        ),
        *(
            (
                "Q9",
                (
                    f"if mode == 'encrypt':\n    answer = {encryption}\n"
                    "else:\n    answer = message[::number + 1]"
                ),
            )
            for encryption in (
                "'0' * (len(message) * (number + 1))",
                "'x' * (len(message) * (number + 1))",
                "''.join(c + '0' * number for c in message)",
                "message",
            )
        ),
        ("Q9", "answer = message[::3]"),
    ),
)
def test_a4_rejects_incorrect_notebook_answers(question_id, source, tmp_path) -> None:
    submission = tmp_path / "A4.ipynb"
    submission.write_bytes(_notebook([f"# A4{question_id}\n{source}"]))

    result = run_question_isolated("A4", question_id, submission)

    assert len(result.cases) == len(get_assignment("A4").question(question_id).cases)
    assert not result.passed
    assert any(not case.passed for case in result.cases)
