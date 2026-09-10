"""Parent-side API for running grader workers with a timeout."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .models import (
    Assignment,
    CaseResult,
    CheckResult,
    QuestionResult,
    resolve_submission,
)
from .registry import get_assignment
from .worker import RESULT_PREFIX


def _question_failure(
    assignment: Assignment,
    question_id: str,
    message: str,
) -> QuestionResult:
    question = assignment.question(question_id)
    cases = tuple(
        CaseResult(case.id, False, (CheckResult(False, message),))
        for case in question.cases
    )
    return QuestionResult(assignment.id, question.id, cases)


def run_question_with_worker(
    assignment: Assignment,
    question_id: str,
    submission: str | Path,
    *,
    worker_module: str,
    timeout: float = 5.0,
) -> QuestionResult:
    """Run one question using an installed worker module."""
    submission_path = resolve_submission(submission)
    if not submission_path.is_file():
        return _question_failure(
            assignment,
            question_id,
            f"Submission file not found: {submission_path}",
        )

    command = [
        sys.executable,
        "-m",
        worker_module,
        assignment.id,
        question_id,
        str(submission_path),
    ]
    environment = os.environ.copy()
    environment.setdefault("MPLBACKEND", "Agg")

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=environment,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _question_failure(
            assignment,
            question_id,
            f"Timed out after {timeout:g} seconds",
        )

    payload = next(
        (
            line.removeprefix(RESULT_PREFIX)
            for line in reversed(completed.stdout.splitlines())
            if line.startswith(RESULT_PREFIX)
        ),
        None,
    )
    if payload is None:
        detail = completed.stderr.strip() or completed.stdout.strip()
        message = "Grader worker exited without returning a result"
        if detail:
            message += f": {detail[-500:]}"
        return _question_failure(assignment, question_id, message)

    try:
        return QuestionResult.from_dict(json.loads(payload))
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        return _question_failure(
            assignment,
            question_id,
            f"Could not read grader result: {error}",
        )


def run_question_isolated(
    assignment_id: str,
    question_id: str,
    submission: str | Path,
    *,
    timeout: float = 5.0,
) -> QuestionResult:
    """Run one question in a disposable child process."""
    assignment = get_assignment(assignment_id)
    return run_question_with_worker(
        assignment,
        question_id,
        submission,
        worker_module="ne111_grader.worker",
        timeout=timeout,
    )


def run_question_source(
    assignment_id: str,
    question_id: str,
    source: bytes,
    *,
    filename: str = "submission.py",
    timeout: float = 5.0,
) -> QuestionResult:
    """Run a question using source uploaded through a browser."""
    safe_name = Path(filename).name
    if not safe_name.lower().endswith(".py"):
        safe_name += ".py"

    with tempfile.TemporaryDirectory(prefix="ne111-upload-") as temporary:
        submission = Path(temporary) / safe_name
        submission.write_bytes(source)
        return run_question_isolated(
            assignment_id,
            question_id,
            submission,
            timeout=timeout,
        )
