"""Public checks for notebook-based Assignment 2."""

from __future__ import annotations

from ..checks import Approx, Equals, Raises, Silent
from ..models import Assignment, Case, Question

ASSIGNMENT = Assignment(
    id="A2",
    title="Assignment 2",
    notebook_submission=True,
    questions=(
        Question(
            id="Q1",
            title="Convert a string to a float",
            input_names=("a",),
            cases=(
                Case("Q1.1", args=("1",), checks=(Approx(1.0), Silent())),
                Case("Q1.2", args=("2.1",), checks=(Approx(2.1),)),
                Case("Q1.3", args=(11,), checks=(Approx(11.0),)),
            ),
        ),
        Question(
            id="Q2",
            title="Convert a string to an int",
            input_names=("a",),
            cases=(
                Case("Q2.1", args=("1",), checks=(Equals(1),)),
                Case("Q2.2", args=("2.1",), checks=(Equals(2),)),
                Case("Q2.3", args=(11,), checks=(Equals(11),)),
            ),
        ),
        Question(
            id="Q3",
            title="Find the remainder of division",
            input_names=("a", "b"),
            cases=(
                Case("Q3.1", args=(4, 3), checks=(Equals(1),)),
                Case("Q3.2", args=(3.4, 1.1), checks=(Approx(0.1),)),
            ),
        ),
        Question(
            id="Q4",
            title="Find whole and decimal portions",
            input_names=("a",),
            cases=(
                Case("Q4.1", args=(1.3,), checks=(Approx((1, 0.3)),)),
                Case("Q4.2", args=(22.0,), checks=(Approx((22, 0)),)),
                Case("Q4.3", args=(12,), checks=(Approx((12, 0)),)),
            ),
        ),
        Question(
            id="Q5",
            title="Find the type and convert it to a string",
            input_names=("a",),
            cases=(
                Case("Q5.1", args=(1,), checks=(Equals("<class 'int'>"),)),
                Case("Q5.2", args=(3.3,), checks=(Equals("<class 'float'>"),)),
                Case("Q5.3", args=(0.5j,), checks=(Equals("<class 'complex'>"),)),
            ),
        ),
        Question(
            id="Q6",
            title="Join two lists",
            input_names=("a", "b"),
            cases=(
                Case(
                    "Q6.1",
                    args=([1, 2, 3], [4, 5, 6]),
                    checks=(Equals([1, 2, 3, 4, 5, 6]),),
                ),
                Case(
                    "Q6.2",
                    args=(["a", "b"], ["c"]),
                    checks=(Equals(["a", "b", "c"]),),
                ),
                Case(
                    "Q6.3",
                    args=(["a", "b"], "c"),
                    checks=(Raises(TypeError),),
                ),
            ),
        ),
        Question(
            id="Q7",
            title="Insert items into a dictionary",
            input_names=("a", "key", "val"),
            cases=(
                Case("Q7.1", args=({}, "k", 10), checks=(Equals({"k": 10}),)),
                Case(
                    "Q7.2",
                    args=({"a": 1}, "b", 2),
                    checks=(Equals({"a": 1, "b": 2}),),
                ),
                Case(
                    "Q7.3",
                    args=({"a": 1}, "a", 2),
                    checks=(Equals({"a": 2}),),
                ),
            ),
        ),
        Question(
            id="Q8",
            title="Remove a value from a list",
            input_names=("a", "val"),
            cases=(
                Case("Q8.1", args=([1, 2, 3], 2), checks=(Equals([1, 3]),)),
                Case(
                    "Q8.2",
                    args=([1, 2, 3, 2], 2),
                    checks=(Equals([1, 3, 2]),),
                ),
                Case(
                    "Q8.3",
                    args=([1, 2, 3], 5),
                    checks=(Raises(ValueError),),
                ),
            ),
        ),
        Question(
            id="Q9",
            title="Extract a sub-list from a list",
            input_names=("a",),
            cases=(
                Case(
                    "Q9.1",
                    args=([1, 2, 3, 4, 5],),
                    checks=(Equals([1, 2]),),
                ),
                Case("Q9.2", args=([1, 2, 3, 4],), checks=(Equals([1, 2]),)),
                Case(
                    "Q9.3",
                    args=([6, 5, 4, 3, 2, 1],),
                    checks=(Equals([6, 5, 4]),),
                ),
            ),
        ),
        Question(
            id="Q10",
            title="Scan and process all list values",
            input_names=("a",),
            cases=(
                Case("Q10.1", args=([1, 2, 3, 4, 5],), checks=(Equals(4),)),
                Case("Q10.2", args=([4, 3, -1, 10],), checks=(Equals(11),)),
                Case(
                    "Q10.3",
                    args=([4, "3", None, 10],),
                    checks=(Raises(TypeError),),
                ),
            ),
        ),
    ),
)
