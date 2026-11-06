"""Exercise A8's function interface, operator coverage, and written restrictions."""

from __future__ import annotations

import textwrap

import pytest
from test_a3_a8_integration import SOURCES

from ne111_checker.isolated import run_question_isolated
from ne111_checker.registry import get_assignment


def test_a8_uses_python_functions() -> None:
    assignment = get_assignment("A8")
    assert assignment.expected_filename == "A8.py"
    assert not assignment.notebook_submission
    assert [question.id for question in assignment.questions] == [
        f"Q{number}" for number in range(1, 8)
    ]


@pytest.mark.parametrize(
    "operation",
    ("add", "subtract", "multiply", "divide", "floor_divide", "mod", "power"),
)
def test_a8_checks_every_operator(tmp_path, operation: str) -> None:
    submission = tmp_path / "A8.py"
    submission.write_text(
        SOURCES["A8"].replace(f"np.{operation}", "np.maximum"), encoding="utf-8"
    )

    result = run_question_isolated("A8", "Q2", submission, timeout=10)

    assert len(result.cases) == 7
    assert not result.passed, result.to_dict()


@pytest.mark.parametrize("variant", ("aliases", "global_dispatch"))
def test_a8_accepts_equivalent_ufunc_references(tmp_path, variant: str) -> None:
    source = SOURCES["A8"]
    if variant == "aliases":
        source = "from numpy import floor_divide as floor\n" + source.replace(
            "np.floor_divide", "floor"
        ).replace("np.divide", "np.true_divide").replace("np.mod", "np.remainder")
    else:
        start = source.index("    operations =")
        stop = source.index("    return operations", start)
        dispatch = source[start:stop]
        source = source.replace(dispatch, "").replace(
            "def A8Q2(", textwrap.dedent(dispatch) + "\ndef A8Q2("
        )
    submission = tmp_path / "A8.py"
    submission.write_text(source, encoding="utf-8")

    result = run_question_isolated("A8", "Q2", submission, timeout=10)

    assert result.passed, result.to_dict()


@pytest.mark.parametrize(
    ("question_id", "original", "replacement"),
    (
        ("Q1", "def A8Q1(", "def A7Q1("),
        ("Q3", "return ((points[:, 0].min()", "return ([points[:, 0].min()"),
        ("Q4", "np.linalg.norm(vector)", "vector.sum()"),
        ("Q5", ".flatten()", ""),
        ("Q6", "matrix[mask].sum()", "None"),
        (
            "Q7",
            " or np.allclose(matrix, np.tril(matrix))",
            "",
        ),
    ),
)
def test_a8_rejects_incorrect_functions(tmp_path, question_id, original, replacement):
    source = SOURCES["A8"].replace(original, replacement)
    if question_id == "Q3":
        source = source.replace("points[:, 1].min()),", "points[:, 1].min()],")
    submission = tmp_path / "A8.py"
    submission.write_text(source, encoding="utf-8")

    result = run_question_isolated("A8", question_id, submission, timeout=10)

    assert not result.passed, result.to_dict()
    if question_id == "Q6":
        assert not any(case.passed for case in result.cases)


@pytest.mark.parametrize(
    ("body", "message"),
    (
        ("return np.trace(A)", "trace"),
        ("return np.asarray(A).trace()", "trace"),
        (
            "total = 0\n    for i in range(len(A)):\n        total += A[i][i]\n    return total",
            "for loop",
        ),
    ),
)
def test_a8_enforces_trace_restrictions(tmp_path, body: str, message: str) -> None:
    submission = tmp_path / "A8.py"
    submission.write_text(
        "import numpy as np\ndef A8Q6(A):\n    " + body + "\n", encoding="utf-8"
    )

    result = run_question_isolated("A8", "Q6", submission, timeout=10)

    assert not any(case.passed for case in result.cases)
    assert any(
        message in check.message
        for case in result.cases
        for check in case.checks
        if not check.passed
    ), result.to_dict()
