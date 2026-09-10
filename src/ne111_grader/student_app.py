"""Generic student-facing Streamlit interface."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from ne111_grader.isolated import run_question_isolated
from ne111_grader.registry import get_assignment


def _format_call(
    function_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
) -> str:
    arguments = [repr(arg) for arg in args]
    arguments.extend(f"{key}={value!r}" for key, value in kwargs.items())
    return f"{function_name}({', '.join(arguments)})"


assignment = get_assignment(os.environ.get("NE111_GRADER_ASSIGNMENT", "A1"))
default_submission = os.environ.get(
    "NE111_GRADER_SUBMISSION",
    str(Path.cwd() / assignment.expected_filename),
)

st.set_page_config(page_title=f"{assignment.id} Grader", page_icon="✅")
st.title(f"{assignment.title} Grader")
st.caption("Each question runs in a separate process with a five-second timeout.")

submission_text = st.text_input("Submission file", value=default_submission)
submission = Path(submission_text).expanduser()

if submission.name != assignment.expected_filename:
    st.warning(f"Your submission should be named `{assignment.expected_filename}`.")
elif not submission.is_file():
    st.info(f"Create `{assignment.expected_filename}` or select its location above.")

tabs = st.tabs([question.id for question in assignment.questions])
for tab, question in zip(tabs, assignment.questions):
    with tab:
        st.subheader(f"{question.id}: {question.title}")
        function_name = f"{assignment.id}{question.id}"
        for case in question.cases:
            st.code(
                _format_call(function_name, case.args, dict(case.kwargs)),
                language="python",
            )

        state_key = f"result-{assignment.id}-{question.id}-{submission}"
        if st.button(f"Run {function_name}", key=f"run-{question.id}"):
            with st.spinner(f"Testing {function_name}..."):
                st.session_state[state_key] = run_question_isolated(
                    assignment.id,
                    question.id,
                    submission,
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
