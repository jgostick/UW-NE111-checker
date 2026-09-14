from __future__ import annotations

from ne111_checker.checks import Approx, Equals, Raises, Silent
from ne111_checker.models import Case
from ne111_checker.runner import run_case


def test_multiple_checks_can_pass() -> None:
    case = Case("example", args=("3.5",), checks=(Approx(3.5), Silent()))

    result = run_case(float, case)

    assert result.passed
    assert len(result.checks) == 2


def test_unexpected_exception_fails() -> None:
    case = Case("example", args=("not a number",), checks=(Equals(3.5),))

    result = run_case(float, case)

    assert not result.passed
    assert "ValueError" in result.checks[0].message


def test_expected_exception_is_independent() -> None:
    case = Case("example", args=("not a number",), checks=(Raises(ValueError),))

    result = run_case(float, case)

    assert result.passed
