from __future__ import annotations

import textwrap

from ne111_grader.isolated import run_question_isolated
from ne111_grader.registry import get_assignment

REFERENCE = """
def A1Q1(x):
    return float(x)

def A1Q2(x):
    return int(float(x))

def A1Q3(x, y):
    return x % y

def A1Q4(x):
    from math import modf
    return modf(float(x))

def A1Q5(x):
    return str(type(x))

def A1Q6(x, y):
    return x + y

def A1Q7(d, k, v):
    d[k] = v
    return d

def A1Q8(values, value):
    values.remove(value)
    return values

def A1Q9(values):
    return values[:len(values) // 2]

def A1Q10(values):
    return max(values) - min(values)
"""


def test_reference_submission_passes_all_public_cases(tmp_path) -> None:
    submission = tmp_path / "A1.py"
    submission.write_text(textwrap.dedent(REFERENCE), encoding="utf-8")
    assignment = get_assignment("A1")

    results = [
        run_question_isolated("A1", question.id, submission)
        for question in assignment.questions
    ]

    assert all(result.passed for result in results)


def test_missing_function_is_reported(tmp_path) -> None:
    submission = tmp_path / "A1.py"
    submission.write_text("def something_else():\n    pass\n", encoding="utf-8")

    result = run_question_isolated("A1", "Q1", submission)

    assert not result.passed
    assert "A1Q1 was not found" in result.cases[0].checks[0].message
