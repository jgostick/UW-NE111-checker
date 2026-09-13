"""Child-process entry point for running untrusted student functions."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

from .models import Assignment, CaseResult, CheckResult, QuestionResult
from .notebooks import NotebookFormatError, load_notebook
from .registry import get_assignment
from .runner import run_case, run_notebook_case

RESULT_PREFIX = "NE111_GRADER_RESULT="


def _failed_case(case_id: str, message: str) -> CaseResult:
    return CaseResult(
        case_id=case_id,
        passed=False,
        checks=(CheckResult(False, message),),
    )


def _load_module(path: Path):
    module_name = f"ne111_submission_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _notebook_inputs(question, case) -> dict[str, object]:
    if len(question.input_names) != len(case.args):
        raise NotebookFormatError(
            f"Notebook inputs for {question.id} are not configured by this assignment"
        )
    inputs = dict(zip(question.input_names, case.args))
    overlap = inputs.keys() & case.kwargs.keys()
    if overlap:
        names = ", ".join(sorted(overlap))
        raise NotebookFormatError(f"Duplicate notebook input name(s): {names}")
    inputs.update(case.kwargs)
    return inputs


def run_question_for_assignment(
    assignment: Assignment, question_id: str, submission: Path
) -> QuestionResult:
    question = assignment.question(question_id)

    with tempfile.TemporaryDirectory(prefix="ne111-grader-") as temporary:
        workdir = Path(temporary)
        copied_submission = workdir / submission.name
        shutil.copy2(submission, copied_submission)
        for fixture in assignment.fixtures:
            fixture_path = workdir / fixture.path
            fixture_path.parent.mkdir(parents=True, exist_ok=True)
            fixture_path.write_text(fixture.contents, encoding="utf-8")

        previous_directory = Path.cwd()
        os.chdir(workdir)
        try:
            if copied_submission.suffix.lower() == ".ipynb":
                try:
                    notebook = load_notebook(copied_submission)
                    answer_source = notebook.answer_for(f"{assignment.id}{question.id}")
                    case_results = []
                    for case in question.cases:
                        with tempfile.TemporaryDirectory(
                            prefix="ne111-notebook-case-"
                        ) as case_temporary:
                            case_workdir = Path(case_temporary)
                            for fixture in assignment.fixtures:
                                fixture_path = case_workdir / fixture.path
                                fixture_path.parent.mkdir(parents=True, exist_ok=True)
                                fixture_path.write_text(
                                    fixture.contents, encoding="utf-8"
                                )
                            os.chdir(case_workdir)
                            case_results.append(
                                run_notebook_case(
                                    notebook.setup_sources,
                                    answer_source,
                                    _notebook_inputs(question, case),
                                    case,
                                )
                            )
                            os.chdir(workdir)
                    cases = tuple(case_results)
                except NotebookFormatError as error:
                    cases = tuple(
                        _failed_case(case.id, str(error)) for case in question.cases
                    )
                return QuestionResult(assignment.id, question.id, cases)

            try:
                module = _load_module(copied_submission)
            except BaseException as error:  # noqa: BLE001 - submission import boundary
                message = f"Could not import {submission.name}: {type(error).__name__}: {error}"
                cases = tuple(_failed_case(case.id, message) for case in question.cases)
                return QuestionResult(assignment.id, question.id, cases)

            function_name = f"{assignment.id}{question.id}"
            try:
                function = getattr(module, function_name)
            except AttributeError:
                message = f"Function {function_name} was not found"
                cases = tuple(_failed_case(case.id, message) for case in question.cases)
                return QuestionResult(assignment.id, question.id, cases)

            cases = tuple(run_case(function, case) for case in question.cases)
            return QuestionResult(assignment.id, question.id, cases)
        finally:
            os.chdir(previous_directory)


def run_question(
    assignment_id: str, question_id: str, submission: Path
) -> QuestionResult:
    """Run a public assignment question in the worker process."""
    assignment = get_assignment(assignment_id)
    return run_question_for_assignment(assignment, question_id, submission)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("assignment")
    parser.add_argument("question")
    parser.add_argument("submission", type=Path)
    args = parser.parse_args(argv)

    try:
        result = run_question(args.assignment, args.question, args.submission.resolve())
    except BaseException as error:  # noqa: BLE001 - worker must always report a result
        assignment = get_assignment(args.assignment)
        question = assignment.question(args.question)
        message = f"Grader worker failed: {type(error).__name__}: {error}"
        cases = tuple(_failed_case(case.id, message) for case in question.cases)
        result = QuestionResult(assignment.id, question.id, cases)

    print(RESULT_PREFIX + json.dumps(result.to_dict()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
