"""Pure in-process execution used by isolated worker processes."""

from __future__ import annotations

import ast
import copy
import inspect
import io
from collections.abc import Callable
from contextlib import redirect_stderr, redirect_stdout

from .models import CallRecord, Case, CaseResult


def _source_with_injected_inputs(source: str, input_names: set[str]) -> ast.Module:
    """Remove top-level student test-value assignments before grading a cell."""
    tree = ast.parse(source)
    body = []
    accepting_test_values = True
    replaced_names: set[str] = set()
    for statement in tree.body:
        if isinstance(statement, (ast.Import, ast.ImportFrom)):
            body.append(statement)
            continue

        targets: list[ast.expr] = []
        if isinstance(statement, ast.Assign):
            targets = statement.targets
        elif isinstance(statement, ast.AnnAssign):
            targets = [statement.target]

        assigned = {
            node.id
            for target in targets
            for node in ast.walk(target)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
        }
        new_test_values = (assigned & input_names) - replaced_names
        if accepting_test_values and new_test_values:
            replaced_names.update(new_test_values)
            continue
        accepting_test_values = False
        body.append(statement)
    tree.body = body
    return ast.fix_missing_locations(tree)


def run_case(function: Callable[..., object], case: Case) -> CaseResult:
    """Run one case and evaluate all of its checks."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    return_value = None
    exception: BaseException | None = None
    try:
        source = inspect.getsource(function)
    except (OSError, TypeError):
        source = ""

    try:
        args = copy.deepcopy(case.args)
        kwargs = copy.deepcopy(dict(case.kwargs))
        with redirect_stdout(stdout), redirect_stderr(stderr):
            return_value = function(*args, **kwargs)
    except BaseException as error:  # noqa: BLE001 - student code may call sys.exit
        exception = error

    record = CallRecord(
        return_value=return_value,
        exception=exception,
        stdout=stdout.getvalue(),
        stderr=stderr.getvalue(),
        source=source,
    )
    results = tuple(check.evaluate(record) for check in case.checks)
    return CaseResult(
        case_id=case.id,
        passed=bool(results) and all(result.passed for result in results),
        checks=results,
    )


def run_notebook_case(
    setup_sources: tuple[str, ...],
    answer_source: str,
    inputs: dict[str, object],
    case: Case,
) -> CaseResult:
    """Execute one tagged notebook cell in a fresh namespace for one case."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    namespace = copy.deepcopy(inputs)
    return_value = None
    exception: BaseException | None = None

    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            for index, source in enumerate(setup_sources, start=1):
                exec(  # noqa: S102 - execute submitted code in the worker process
                    compile(source, f"<setup cell {index}>", "exec"), namespace
                )
            exec(  # noqa: S102 - execute submitted code in the worker process
                compile(
                    _source_with_injected_inputs(answer_source, set(inputs)),
                    "<answer cell>",
                    "exec",
                ),
                namespace,
            )
            if "answer" not in namespace:
                raise NameError("The answer cell did not assign a value to answer")
            return_value = namespace["answer"]
    except BaseException as error:  # noqa: BLE001 - student execution boundary
        exception = error

    record = CallRecord(
        return_value=return_value,
        exception=exception,
        stdout=stdout.getvalue(),
        stderr=stderr.getvalue(),
        source=answer_source,
    )
    results = tuple(check.evaluate(record) for check in case.checks)
    return CaseResult(
        case_id=case.id,
        passed=bool(results) and all(result.passed for result in results),
        checks=results,
    )
