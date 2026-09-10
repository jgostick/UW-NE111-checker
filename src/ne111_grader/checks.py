"""Reusable checks for function return values and behavior."""

from __future__ import annotations

import ast
import csv
import textwrap
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
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


@dataclass(frozen=True)
class AvoidsSyntax:
    """Check that a function's parsed source omits a Python syntax node."""

    forbidden: type[ast.AST]
    label: str

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        tree, error = _parse_source(record)
        if error:
            return error
        if any(isinstance(node, self.forbidden) for node in ast.walk(tree)):
            return CheckResult(False, f"Used forbidden syntax: {self.label}")
        return CheckResult(True, f"Avoided forbidden syntax: {self.label}")


@dataclass(frozen=True)
class UsesCall:
    """Check for a function or method call by its final attribute name."""

    name: str

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        tree, error = _parse_source(record)
        if error:
            return error
        if any(_call_name(node) == self.name for node in ast.walk(tree)):
            return CheckResult(True, f"Called {self.name} as required")
        return CheckResult(False, f"Did not call {self.name} as required")


@dataclass(frozen=True)
class UsesSymbol:
    """Check for a name or attribute reference, including indirect calls."""

    name: str

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        tree, error = _parse_source(record)
        if error:
            return error
        found = any(
            (isinstance(node, ast.Name) and node.id == self.name)
            or (isinstance(node, ast.Attribute) and node.attr == self.name)
            for node in ast.walk(tree)
        )
        if found:
            return CheckResult(True, f"Used {self.name} as required")
        return CheckResult(False, f"Did not use {self.name} as required")


@dataclass(frozen=True)
class AvoidsCall:
    """Check that a function or method is not called."""

    name: str

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        tree, error = _parse_source(record)
        if error:
            return error
        if any(_call_name(node) == self.name for node in ast.walk(tree)):
            return CheckResult(False, f"Called forbidden function {self.name}")
        return CheckResult(True, f"Did not call forbidden function {self.name}")


def _parse_source(record: CallRecord) -> tuple[ast.AST, CheckResult | None]:
    if not record.source:
        return ast.Module(body=[], type_ignores=[]), CheckResult(
            False, "Could not inspect the function source"
        )
    try:
        return ast.parse(textwrap.dedent(record.source)), None
    except SyntaxError as error:
        return ast.Module(body=[], type_ignores=[]), CheckResult(
            False, f"Could not parse the function source: {error}"
        )


def _call_name(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


@dataclass(frozen=True)
class SourceEquals:
    expected: str

    def evaluate(self, record: CallRecord) -> CheckResult:
        actual = textwrap.dedent(record.source).strip()
        expected = textwrap.dedent(self.expected).strip()
        if actual == expected:
            return CheckResult(True, "Function source has the expected formatting")
        return CheckResult(
            False, "Function source does not have the expected formatting"
        )


@dataclass(frozen=True)
class DocstringContains:
    required: tuple[str, ...]

    def evaluate(self, record: CallRecord) -> CheckResult:
        tree, error = _parse_source(record)
        if error:
            return error
        function = next(
            (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)), None
        )
        docstring = ast.get_docstring(function) if function is not None else None
        missing = [text for text in self.required if text not in (docstring or "")]
        if missing:
            return CheckResult(False, f"Docstring is missing: {', '.join(missing)}")
        return CheckResult(True, "Docstring contains all required sections")


@dataclass(frozen=True)
class DTypeIs:
    expected: type[Any]

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        dtype = getattr(record.return_value, "dtype", None)
        if dtype is None:
            return CheckResult(False, "Returned value has no dtype")
        if dtype == self.expected:
            return CheckResult(True, f"Returned dtype {dtype}")
        return CheckResult(
            False, f"Expected dtype {self.expected.__name__}, got {dtype}"
        )


@dataclass(frozen=True)
class ItemAt:
    index: int
    check: Any

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            value = record.return_value[self.index]
        except (IndexError, KeyError, TypeError) as error:
            return CheckResult(False, f"Could not access item {self.index}: {error}")
        return self.check.evaluate(replace(record, return_value=value))


@dataclass(frozen=True)
class Attribute:
    name: str
    check: Any

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            value = getattr(record.return_value, self.name)
        except AttributeError as error:
            return CheckResult(False, str(error))
        return self.check.evaluate(replace(record, return_value=value))


@dataclass(frozen=True)
class HasAttribute:
    name: str

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        if hasattr(record.return_value, self.name):
            return CheckResult(True, f"Returned value has attribute {self.name}")
        return CheckResult(False, f"Returned value has no attribute {self.name}")


@dataclass(frozen=True)
class MethodResult:
    name: str
    check: Any

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            value = getattr(record.return_value, self.name)()
        except (AttributeError, TypeError, ValueError) as error:
            return CheckResult(False, f"Could not call {self.name}: {error}")
        return self.check.evaluate(replace(record, return_value=value))


@dataclass(frozen=True)
class MinIs:
    expected: Any

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            actual = min(_flatten(record.return_value))
        except (TypeError, ValueError) as error:
            return CheckResult(False, f"Could not find minimum: {error}")
        return Equals(self.expected).evaluate(replace(record, return_value=actual))


@dataclass(frozen=True)
class MaxIs:
    expected: Any

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            actual = max(_flatten(record.return_value))
        except (TypeError, ValueError) as error:
            return CheckResult(False, f"Could not find maximum: {error}")
        return Equals(self.expected).evaluate(replace(record, return_value=actual))


def _flatten(value: Any) -> list[Any]:
    try:
        return list(np.asarray(value).ravel())
    except (TypeError, ValueError):
        pass
    flattened: list[Any] = []
    for item in value:
        if isinstance(item, (list, tuple)):
            flattened.extend(_flatten(item))
        else:
            flattened.append(item)
    return flattened


@dataclass(frozen=True)
class TextFileEquals:
    path: str
    expected: str

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            actual = Path(self.path).read_text(encoding="utf-8")
        except OSError as error:
            return CheckResult(False, f"Could not read {self.path}: {error}")
        if actual == self.expected:
            return CheckResult(True, f"Wrote the expected contents to {self.path}")
        return CheckResult(False, f"Unexpected contents in {self.path}")


@dataclass(frozen=True)
class LastLineIs:
    path: str
    expected: str

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            lines = Path(self.path).read_text(encoding="utf-8").splitlines()
        except OSError as error:
            return CheckResult(False, f"Could not read {self.path}: {error}")
        actual = lines[-1] if lines else ""
        return Equals(self.expected).evaluate(replace(record, return_value=actual))


@dataclass(frozen=True)
class CsvEquals:
    path: str
    expected: dict[str, list[Any]]

    def evaluate(self, record: CallRecord) -> CheckResult:
        failure = _unexpected_exception(record)
        if failure:
            return failure
        try:
            with Path(self.path).open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))
        except OSError as error:
            return CheckResult(False, f"Could not read {self.path}: {error}")
        actual = {
            column: [_coerce_csv_value(row[column]) for row in rows]
            for column in self.expected
        }
        return Equals(self.expected).evaluate(replace(record, return_value=actual))


def _coerce_csv_value(value: str) -> Any:
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value
