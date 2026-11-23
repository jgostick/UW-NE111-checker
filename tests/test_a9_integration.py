"""Regression coverage for the public plotting cases."""

from __future__ import annotations

from textwrap import dedent

import pytest

from ne111_checker.isolated import run_question_isolated


@pytest.mark.parametrize(
    ("question", "source"),
    (
        (
            "Q1",
            """
            def A9Q1(x, y):
                fig, ax = plt.subplots()
                ax.scatter(y, x)
                return fig, ax
            """,
        ),
        (
            "Q2",
            """
            def A9Q2(*arrays):
                fig, axes = plt.subplots(len(arrays), 1)
                for ax, array in zip(axes, arrays):
                    ax.hist(array)
                return fig, axes
            """,
        ),
        (
            "Q3",
            """
            def A9Q3(im):
                fig, ax = plt.subplots()
                ax.imshow(im.T)
                return fig, ax
            """,
        ),
        (
            "Q4",
            """
            def A9Q4(fig, color):
                fig.axes[0].set_facecolor(color)
                return fig
            """,
        ),
        (
            "Q5",
            """
            def A9Q5(x, y):
                keep = (x >= 0) & (x <= 1)
                fig, ax = plt.subplots()
                ax.scatter(x[keep], y[keep])
                return fig, ax
            """,
        ),
    ),
)
def test_plotting_mistakes_fail_without_worker_errors(tmp_path, question, source):
    submission = tmp_path / "A9.py"
    submission.write_text("import matplotlib.pyplot as plt\n" + dedent(source))

    result = run_question_isolated("A9", question, submission, timeout=10)

    (case,) = result.cases
    assert not case.passed
    assert any(check.passed for check in case.checks)
    assert not any("worker" in check.message.lower() for check in case.checks)
