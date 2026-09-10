"""Reusable checks for function return values and behavior."""

from __future__ import annotations

import ast
import textwrap
from dataclasses import dataclass
from typing import Any

from numpy.testing import assert_allclose, assert_equal

from .models import CallRecord, CheckResult


def _unexpected_exception(record: CallRecord) -> CheckResult | None:
    if record.exception is None:
        return None
    name = type(record.exception).__name__
    return CheckResult(False, f"Raised {name}: {record.exception}")


@dataclass(frozen=True)
class Equals:
    expected: Any

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            assert_equal(record.return_value, self.expected)
        except AssertionError as error:
            return CheckResult(False, str(error))
        return CheckResult(True, f"Returned the expected value: {self.expected!r}")


@dataclass(frozen=True)
class Approx:
    expected: Any
    rtol: float = 1e-7
    atol: float = 0.0

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            assert_allclose(
                record.return_value,
                self.expected,
                rtol=self.rtol,
                atol=self.atol,
            )
        except (AssertionError, TypeError, ValueError) as error:
            return CheckResult(False, str(error))
        return CheckResult(True, "Returned the expected value within tolerance")


@dataclass(frozen=True)
class Raises:
    expected: type[BaseException] | tuple[type[BaseException], ...]

    def evaluate(self, record: CallRecord) -> CheckResult:
        expected_names = (
            self.expected.__name__
            if isinstance(self.expected, type)
            else " or ".join(item.__name__ for item in self.expected)
        )
        if record.exception is None:
            return CheckResult(
                False, f"Expected {expected_names}, but nothing was raised"
            )
        if not isinstance(record.exception, self.expected):
            actual = type(record.exception).__name__
            return CheckResult(False, f"Expected {expected_names}, but raised {actual}")
        return CheckResult(
            True, f"Raised {type(record.exception).__name__} as expected"
        )


@dataclass(frozen=True)
class Silent:
    def evaluate(self, record: CallRecord) -> CheckResult:
        if record.stdout == "":
            return CheckResult(True, "Did not print to standard output")
        return CheckResult(False, f"Printed unexpectedly: {record.stdout!r}")


@dataclass(frozen=True)
class LengthIs:
    expected: int

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            actual = len(record.return_value)
        except TypeError as error:
            return CheckResult(False, str(error))
        if actual != self.expected:
            return CheckResult(False, f"Expected length {self.expected}, got {actual}")
        return CheckResult(True, f"Returned an object of length {self.expected}")


@dataclass(frozen=True)
class TypeIs:
    expected: type[Any]

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        actual = type(record.return_value)
        if actual is not self.expected:
            return CheckResult(
                False,
                f"Expected type {self.expected.__name__}, got {actual.__name__}",
            )
        return CheckResult(True, f"Returned type {self.expected.__name__}")


@dataclass(frozen=True)
class UsesSyntax:
    """Check a function's parsed source for a required Python syntax node."""

    expected: type[ast.AST]
    label: str

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        if not record.source:
            return CheckResult(False, "Could not inspect the function source")
        try:
            tree = ast.parse(textwrap.dedent(record.source))
        except SyntaxError as error:
            return CheckResult(False, f"Could not parse the function source: {error}")
        if any(isinstance(node, self.expected) for node in ast.walk(tree)):
            return CheckResult(True, f"Used the required syntax: {self.label}")
        return CheckResult(False, f"Did not use the required syntax: {self.label}")
