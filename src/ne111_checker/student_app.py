"""Generic student-facing Streamlit interface."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from ne111_checker.isolated import run_question_isolated
from ne111_checker.registry import get_assignment


def _format_call(
    function_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
) -> str:
    arguments = [repr(arg) for arg in args]
    arguments.extend(f"{key}={value!r}" for key, value in kwargs.items())
    return f"{function_name}({', '.join(arguments)})"


def _format_notebook_inputs(question, case) -> str:
    values = [
        f"{name} = {value!r}" for name, value in zip(question.input_names, case.args)
    ]
    values.extend(f"{key} = {value!r}" for key, value in case.kwargs.items())
    return "\n".join(values) if values else "No checker-supplied inputs"


assignment = get_assignment(os.environ.get("NE111_GRADER_ASSIGNMENT", "A1"))
default_submission = os.environ.get(
    "NE111_GRADER_SUBMISSION",
    str(Path.cwd() / assignment.expected_filename),
)

st.set_page_config(page_title=f"{assignment.id} Checker", page_icon="✅")
st.title(f"{assignment.title} Checker")
st.caption("Each question runs in a separate process with a five-second timeout.")

configured_submission = Path(default_submission).expanduser()

if configured_submission.is_file():
    submission_key = (
        f"{configured_submission.resolve()}-{configured_submission.stat().st_mtime_ns}"
    )
    submission_label = configured_submission.name
    submission_path = configured_submission
    st.caption(
        f"Using `{configured_submission}`. Save the file, then run a question again "
        "to check its latest contents."
    )
else:
    submission_key = "none"
    submission_label = "Notebook not found"
    submission_path = None
    st.info(
        f"Save `{assignment.expected_filename}` in the folder where you launched "
        "the checker, then restart the checker."
    )

tabs = st.tabs([question.id for question in assignment.questions])
for tab, question in zip(tabs, assignment.questions):
    with tab:
        st.subheader(f"{question.id}: {question.title}")
        function_name = f"{assignment.id}{question.id}"
        for case in question.cases:
            st.code(
                (
                    _format_notebook_inputs(question, case)
                    if assignment.notebook_submission
                    else _format_call(function_name, case.args, dict(case.kwargs))
                ),
                language="python",
            )

        state_key = f"result-{assignment.id}-{question.id}-{submission_key}"
        if st.button(
            (
                f"Run {function_name} cell"
                if assignment.notebook_submission
                else f"Run {function_name}"
            ),
            key=f"run-{question.id}",
            disabled=submission_path is None,
        ):
            with st.spinner(f"Testing {function_name}..."):
                st.session_state[state_key] = run_question_isolated(
                    assignment.id,
                    question.id,
                    submission_path,
                    timeout=5.0,
                )

        result = st.session_state.get(state_key)
        if result is not None:
            for case_result in result.cases:
                with st.container(border=True):
                    st.markdown(f"**{case_result.case_id}**")
                    for check in case_result.checks:
                        if check.passed:
                            st.success(check.message, icon="✅")
                        else:
                            st.error(check.message, icon="🚨")
