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
            title="Build a greeting",
            input_names=("greeting", "target"),
            cases=(
                Case("Q2.1", args=("Hello", "World"), checks=(Equals("Hello World"),)),
            ),
        ),
        Question(
            id="Q3",
            title="Reassign a variable",
            input_names=("starting_x",),
            cases=(Case("Q3.1", args=(10,), checks=(Equals(47),)),),
        ),
        Question(
            id="Q4",
            title="Swap two values",
            input_names=("x", "y"),
            cases=(Case("Q4.1", args=(10, 20), checks=(Equals((20, 10)),)),),
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
            input_names=("ceiling_value", "floor_value", "logarithm_value"),
            cases=(
                Case(
                    "Q6.1",
                    args=(4.3, 4.8, 1000),
                    checks=(Equals((5, 4, 3.0)), UsesSymbol("math")),
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
            title="Circle area and circumference",
            input_names=("radius",),
            cases=(
                Case(
                    "Q8.1",
                    args=(2,),
                    checks=(Approx((4 * 3.141592653589793, 4 * 3.141592653589793)),),
                ),
            ),
        ),
        Question(
            id="Q9",
            title="Types and conversion",
            input_names=(
                "integer_value",
                "float_value",
                "text_value",
                "boolean_value",
            ),
            cases=(
                Case(
                    "Q9.1",
                    args=(42, 3.14, "100", True),
                    checks=(Equals(("int", "float", "str", "bool", 100, 100.0)),),
                ),
            ),
        ),
        Question(
            id="Q10",
            title="Division operators",
            input_names=("dividend", "divisor"),
            cases=(Case("Q10.1", args=(17, 4), checks=(Approx((4.25, 4, 1)),)),),
        ),
        Question(
            id="Q11",
            title="Exponents and multiplication",
            cases=(
                Case(
                    "Q11.1",
                    checks=(Equals((81, 81, True)), UsesSymbol("exponent")),
                ),
            ),
        ),
        Question(
            id="Q12",
            title="Multiple assignment",
            cases=(
                Case(
                    "Q12.1",
                    checks=(Equals((2, 3, 4, 5, 5, 5, 9, 125)),),
                ),
            ),
        ),
        Question(
            id="Q13",
            title="Operator precedence",
            cases=(Case("Q13.1", checks=(Approx((14, 20, 7, 2)),)),),
        ),
        Question(
            id="Q14",
            title="Negative numbers",
            input_names=("positive_num", "negative_num"),
            cases=(
                Case(
                    "Q14.1",
                    args=(10, -7),
                    checks=(Approx((3, 17, -70, -10 / 7, 7)),),
                ),
            ),
        ),
    ),
)
