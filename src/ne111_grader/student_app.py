"""Generic student-facing Streamlit interface."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import streamlit as st

from ne111_grader.isolated import run_question_isolated, run_question_source
from ne111_grader.registry import get_assignment


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

st.set_page_config(page_title=f"{assignment.id} Grader", page_icon="✅")
st.title(f"{assignment.title} Grader")
st.caption("Each question runs in a separate process with a five-second timeout.")

configured_submission = Path(
    st.text_input(
        "Local submission path",
        value=default_submission,
        help=(
            "Recommended: enter the path to your saved notebook. The grader rereads "
            "this file every time you run a question."
        ),
    )
).expanduser()
uploaded_submission = st.file_uploader(
    "Or upload a one-time copy",
    type=("ipynb",) if assignment.notebook_submission else ("py",),
    help=(
        "Use this only when the local path above is unavailable. Save changes and "
        "upload the file again to check them."
        if assignment.notebook_submission
        else "Use this only when the local path above is unavailable."
    ),
)

if configured_submission.is_file():
    uploaded_source = None
    submission_key = (
        f"{configured_submission.resolve()}-{configured_submission.stat().st_mtime_ns}"
    )
    submission_label = configured_submission.name
    submission_path = configured_submission
    st.caption(
        f"Using `{configured_submission}`. Save the file, then run a question again "
        "to check its latest contents."
    )
elif uploaded_submission is not None:
    uploaded_source = uploaded_submission.getvalue()
    submission_key = hashlib.sha256(uploaded_source).hexdigest()[:12]
    submission_label = uploaded_submission.name
    submission_path = None
else:
    uploaded_source = None
    submission_key = "none"
    submission_label = "No file selected"
    submission_path = None
    st.info(
        "Enter the path to your Jupyter notebook above, or upload a copy."
        if assignment.notebook_submission
        else "Browse for the Python file containing your assignment functions."
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
            disabled=uploaded_source is None and submission_path is None,
        ):
            with st.spinner(f"Testing {function_name}..."):
                if uploaded_source is not None:
                    st.session_state[state_key] = run_question_source(
                        assignment.id,
                        question.id,
                        uploaded_source,
                        filename=submission_label,
                        timeout=5.0,
                    )
                else:
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
