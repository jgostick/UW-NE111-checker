from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_student_app_runs_a_question(monkeypatch, tmp_path) -> None:
    submission = tmp_path / "my_solution.ipynb"
    submission.write_text(
        json.dumps(
            {
                "nbformat": 4,
                "nbformat_minor": 5,
                "metadata": {},
                "cells": [
                    {
                        "cell_type": "code",
                        "metadata": {},
                        "source": "# A1Q1\nanswer = a % b",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("NE111_GRADER_ASSIGNMENT", "A1")
    monkeypatch.setenv("NE111_GRADER_SUBMISSION", str(submission))

    app_spec = importlib.util.find_spec("ne111_checker.student_app")
    assert app_spec is not None and app_spec.origin is not None

    app = AppTest.from_file(Path(app_spec.origin)).run(timeout=10)
    app.button[0].click().run(timeout=10)

    assert not app.exception
    assert not app.error
    assert len(app.tabs) == 10
    assert len(app.success) == 2
