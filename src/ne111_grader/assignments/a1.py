"""Public checks for notebook-based Assignment 1."""

from __future__ import annotations

from ..checks import Approx, Equals, UsesSymbol
from ..models import Assignment, Case, Question

ASSIGNMENT = Assignment(
    id="A1",
    title="Assignment 1",
    notebook_submission=True,
    questions=(
        Question(
            id="Q1",
            title="Remainder",
            input_names=("a", "b"),
            cases=(
                Case("Q1.1", args=(17, 4), checks=(Equals(1),)),
                Case("Q1.2", args=(7.5, 2.0), checks=(Approx(1.5),)),
            ),
        ),
        Question(
            id="Q2",
            title="Operator precedence",
            input_names=("a", "b", "c"),
            cases=(Case("Q2.1", args=(2, 3, 4), checks=(Equals(14),)),),
        ),
        Question(
            id="Q3",
            title="Reassign a variable",
            input_names=("starting_value", "scale", "offset"),
            cases=(Case("Q3.1", args=(10, 5, -3), checks=(Equals(47),)),),
        ),
        Question(
            id="Q4",
            title="Swap two values",
            input_names=("starting_x", "starting_y"),
            cases=(Case("Q4.1", args=(2, 3), checks=(Equals(9),)),),
        ),
        Question(
            id="Q5",
            title="Convert Celsius to Fahrenheit",
            input_names=("celsius",),
            cases=(Case("Q5.1", args=(22.0,), checks=(Approx(71.6),)),),
        ),
        Question(
            id="Q6",
            title="Use the math library",
            input_names=("value",),
            cases=(
                Case(
                    "Q6.1",
                    args=(4.8,),
                    checks=(Approx(5 + 4 + 0.6812412373755872), UsesSymbol("math")),
                ),
            ),
        ),
        Question(
            id="Q7",
            title="Calculate an nth root",
            input_names=("number", "root"),
            cases=(Case("Q7.1", args=(32, 5), checks=(Approx(2.0),)),),
        ),
        Question(
            id="Q8",
            title="Circle area",
            input_names=("radius",),
            cases=(
                Case(
                    "Q8.1",
                    args=(2,),
                    checks=(Approx(4 * 3.141592653589793),),
                ),
            ),
        ),
        Question(
            id="Q9",
            title="Types and conversion",
            input_names=("value",),
            cases=(
                Case(
                    "Q9.1",
                    args=(3.14,),
                    checks=(Equals("<class 'float'>"),),
                ),
            ),
        ),
        Question(
            id="Q10",
            title="Absolute difference",
            input_names=("a", "b"),
            cases=(Case("Q10.1", args=(17, 4), checks=(Equals(13),)),),
        ),
    ),
)
