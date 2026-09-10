from __future__ import annotations

import textwrap

from ne111_grader.isolated import run_question_isolated
from ne111_grader.registry import assignment_ids, get_assignment

REFERENCE = """
def A2Q1(a, b, c):
    return a < b < c

def A2Q2(temperature):
    return 0 <= temperature <= 100

def A2Q3(a, b, relation):
    if relation == ">": return a > b
    if relation == "<": return a < b
    if relation == "==": return a == b
    if relation == "<=": return a <= b
    if relation == ">=": return a >= b
    if relation == "!=": return a != b

def A2Q4(values):
    count = 0
    for value in values:
        if value % 2 == 0:
            count += 1
    return count

def A2Q5(dictionary, key):
    return key in dictionary.keys()

def A2Q6(value):
    return type(value) in (int, float, complex)

def A2Q7(values):
    for value in values:
        if type(value) is int:
            return True
    return False

def A2Q8(values):
    for index in range(len(values) - 1):
        if values[index] > values[index + 1]:
            return False
    return True
"""


def test_public_a2_reference_passes(tmp_path) -> None:
    submission = tmp_path / "A2.py"
    submission.write_text(textwrap.dedent(REFERENCE), encoding="utf-8")
    assignment = get_assignment("A2")

    results = tuple(
        run_question_isolated("A2", question.id, submission)
        for question in assignment.questions
    )

    assert all(result.passed for result in results)
    assert sum(len(result.cases) for result in results) == 27
    assert assignment_ids() == ("A1", "A2")
