"""Whitespace checks accept valid alternatives and identify spacing mistakes."""

from __future__ import annotations

import pytest

from ne111_checker.checks import Pep8Whitespace
from ne111_checker.models import CallRecord


@pytest.mark.parametrize(
    "source",
    (
        "def example(a, b=1):\n    return (a + b, a - b)\n",
        "def example(a, b=1):\n    return a + b, a - b\n",
        "def example(a, b=1):\n    return a**2 + b**2\n",
        "def example(a, b=1):\n    return a ** 2 + b ** 2\n",
    ),
)
def test_accepts_pep8_alternatives(source: str) -> None:
    assert Pep8Whitespace().evaluate(CallRecord(source=source)).passed


@pytest.mark.parametrize(
    ("source", "code"),
    (
        ("def example(a, b = 1):\n    return a + b\n", "E251"),
        ("def example(a):\n    result=a+1\n    return result\n", "E225"),
        ("def example(a):\n    return( a )\n", "E201"),
        ("def example(a):\n  return a\n", "E111"),
        ("def example(a):\n    return a # comment\n", "E261"),
    ),
)
def test_reports_spacing_errors(source: str, code: str) -> None:
    result = Pep8Whitespace().evaluate(CallRecord(source=source))
    assert not result.passed
    assert code in result.message


def test_missing_source_is_a_failure() -> None:
    assert not Pep8Whitespace().evaluate(CallRecord()).passed
