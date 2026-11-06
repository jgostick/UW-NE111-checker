"""Check the introductory NumPy function contract and actionable failures."""

from __future__ import annotations

import pytest
from test_a3_a8_integration import SOURCES

from ne111_checker.isolated import run_question_isolated
from ne111_checker.registry import get_assignment


def test_a7_uses_python_functions() -> None:
    assignment = get_assignment("A7")
    assert assignment.expected_filename == "A7.py"
    assert not assignment.notebook_submission
    assert [question.id for question in assignment.questions] == [
        f"Q{number}" for number in range(1, 9)
    ]


@pytest.mark.parametrize(
    ("question_id", "original", "replacement"),
    (
        ("Q1", ".astype(int)", ".round().astype(int)"),
        ("Q2", "return np.column_stack", "return np.vstack"),
        (
            "Q3",
            "return [[array[:row, :column]",
            "return [[array[:row, :column].tolist()",
        ),
        (
            "Q4",
            "return ((array < threshold).sum()",
            "return [(array < threshold).sum()",
        ),
        ("Q5", "return (array - array.min())", "return (array + array.min())"),
        ("Q6", "axis=0", "axis=1"),
        ("Q7", "len(answers) == 1", "len(answers) >= 1"),
        ("Q8", "array % 2 == 0", "array % 2 != 0"),
        ("Q1", "def A7Q1(", "def A6Q1("),
    ),
)
def test_a7_rejects_incorrect_functions(tmp_path, question_id, original, replacement):
    source = SOURCES["A7"].replace(original, replacement)
    # Complete the tuple-to-list edit for Q4 without introducing a syntax error.
    if question_id == "Q4":
        source = source.replace(
            "(array > threshold).sum())", "(array > threshold).sum()]"
        )
    submission = tmp_path / "A7.py"
    submission.write_text(source, encoding="utf-8")

    result = run_question_isolated("A7", question_id, submission, timeout=10)

    assert not result.passed, result.to_dict()
    assert result.cases
    assert all(case.checks for case in result.cases)


@pytest.mark.parametrize(
    ("question_id", "source", "message"),
    (
        (
            "Q3",
            """
import numpy as np
def A7Q3(arr, split):
    rows = np.split(arr, [split[0]], axis=0)
    return [np.split(row, [split[1]], axis=1) for row in rows]
""",
            "slice notation",
        ),
        (
            "Q4",
            """
import numpy as np
def A7Q4(arr, threshold):
    counts = [0, 0, 0]
    for value in np.asarray(arr).flat:
        counts[0 if value < threshold else 1 if value == threshold else 2] += 1
    return tuple(counts)
""",
            "for loop",
        ),
        (
            "Q8",
            """
import numpy as np
def A7Q8(arr):
    total = 0
    for value in np.asarray(arr).flat:
        if value % 2 == 0:
            total += value
    return total
""",
            "for loop",
        ),
    ),
)
def test_a7_enforces_written_syntax_rules(tmp_path, question_id, source, message):
    submission = tmp_path / "A7.py"
    submission.write_text(source, encoding="utf-8")

    result = run_question_isolated("A7", question_id, submission, timeout=10)

    assert not result.passed
    assert any(
        message in check.message
        for case in result.cases
        for check in case.checks
        if not check.passed
    ), result.to_dict()
