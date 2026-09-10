"""Public checks for Assignment 2."""

from __future__ import annotations

from ..checks import Equals, Raises, Silent
from ..models import Assignment, Case, Question

ASSIGNMENT = Assignment(
    id="A2",
    title="Assignment 2",
    questions=(
        Question(
            id="Q1",
            title="Check whether three values are increasing",
            cases=(
                Case("Q1.1", args=(2, 3, 5), checks=(Equals(True),)),
                Case("Q1.2", args=(4, 3, 6), checks=(Equals(False), Silent())),
                Case("Q1.3", args=("a", 1, 3), checks=(Raises(TypeError),)),
            ),
        ),
        Question(
            id="Q2",
            title="Check whether water is liquid",
            cases=(
                Case("Q2.1", args=(50,), checks=(Equals(True),)),
                Case("Q2.2", args=(110,), checks=(Equals(False),)),
                Case("Q2.3", args=(0,), checks=(Equals(True),)),
                Case("Q2.4", args=(-11,), checks=(Equals(False),)),
            ),
        ),
        Question(
            id="Q3",
            title="Apply a relational operator",
            cases=(
                Case("Q3.1", args=(1, 2, "=="), checks=(Equals(False),)),
                Case("Q3.2", args=(1, 2, ">"), checks=(Equals(False),)),
                Case("Q3.3", args=(1, 2, "<="), checks=(Equals(True),)),
            ),
        ),
        Question(
            id="Q4",
            title="Count even values in a list",
            cases=(
                Case("Q4.1", args=([1, 2, 4, 11],), checks=(Equals(2),)),
                Case("Q4.2", args=([1, 2, 4, "11"],), checks=(Raises(TypeError),)),
            ),
        ),
        Question(
            id="Q5",
            title="Check whether a key is in a dictionary",
            cases=(
                Case("Q5.1", args=({"a": 1, "b": 2}, "a"), checks=(Equals(True),)),
                Case("Q5.2", args=({"a": 1, "b": 2}, "c"), checks=(Equals(False),)),
                Case(
                    "Q5.3",
                    args=(1, "c"),
                    checks=(Raises((AttributeError, TypeError)),),
                ),
                Case(
                    "Q5.4",
                    args=([1, 2], "c"),
                    checks=(Raises((AttributeError, TypeError)),),
                ),
            ),
        ),
        Question(
            id="Q6",
            title="Check whether a value is a number",
            cases=(
                Case("Q6.1", args=(1,), checks=(Equals(True),)),
                Case("Q6.2", args=(2.2,), checks=(Equals(True),)),
                Case("Q6.3", args=("1",), checks=(Equals(False),)),
                Case("Q6.4", args=(False,), checks=(Equals(False),)),
                Case("Q6.5", args=([1, 2],), checks=(Equals(False),)),
            ),
        ),
        Question(
            id="Q7",
            title="Check whether a list contains an integer",
            cases=(
                Case("Q7.1", args=([2.2, "a", 4],), checks=(Equals(True),)),
                Case("Q7.2", args=([2.2, "a", 4.0],), checks=(Equals(False),)),
                Case("Q7.3", args=(20,), checks=(Raises(TypeError),)),
            ),
        ),
        Question(
            id="Q8",
            title="Check whether a list is ordered",
            cases=(
                Case("Q8.1", args=([1, 2, 4, 3],), checks=(Equals(False),)),
                Case("Q8.2", args=([1, 2, 3, 4],), checks=(Equals(True),)),
                Case("Q8.3", args=([1, 2, "3"],), checks=(Raises(TypeError),)),
            ),
        ),
    ),
)
