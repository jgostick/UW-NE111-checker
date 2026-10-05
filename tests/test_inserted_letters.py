"""Check encryption structure while allowing different random filler letters."""

from __future__ import annotations

import pytest

from ne111_checker.checks import InsertedLetters
from ne111_checker.models import CallRecord


@pytest.mark.parametrize("value", ("HabixY", "HzziaB", "HéÅi中Z"))
def test_accepts_different_inserted_letters(value) -> None:
    assert InsertedLetters("Hi", 2).evaluate(CallRecord(return_value=value)).passed


@pytest.mark.parametrize(
    ("value", "feedback"),
    (
        (None, "string"),
        (["H", "a", "b", "i", "x", "Y"], "string"),
        ("Hi", "6 characters"),
        ("HabixYZ", "6 characters"),
        ("abcdef", "original letter"),
        ("H00i00", "only letters"),
        ("H!!i!!", "only letters"),
        ("H  i  ", "only letters"),
    ),
)
def test_rejects_incorrect_encryption_with_feedback(value, feedback) -> None:
    result = InsertedLetters("Hi", 2).evaluate(CallRecord(return_value=value))

    assert not result.passed
    assert feedback in result.message


@pytest.mark.parametrize(("message", "number"), (("go", 0), ("", 2)))
def test_accepts_zero_insertions_and_empty_message(message, number) -> None:
    assert (
        InsertedLetters(message, number)
        .evaluate(CallRecord(return_value=message))
        .passed
    )


def test_reports_submission_exception() -> None:
    result = InsertedLetters("Hi", 2).evaluate(
        CallRecord(exception=RuntimeError("example failure"))
    )

    assert not result.passed
    assert "RuntimeError: example failure" in result.message
