from __future__ import annotations

import ast

from ne111_grader.checks import UsesSyntax
from ne111_grader.models import CallRecord


def test_uses_syntax_finds_ast_node() -> None:
    record = CallRecord(source="def example(items):\n    return 1 in items\n")

    result = UsesSyntax(ast.In, "the in operator").evaluate(record)

    assert result.passed


def test_uses_syntax_rejects_missing_ast_node() -> None:
    record = CallRecord(source="def example(items):\n    return bool(items)\n")

    result = UsesSyntax(ast.For, "a for loop").evaluate(record)

    assert not result.passed
