"""Public checks for Assignment 6."""

from __future__ import annotations

from ..checks import Approx, DocstringContains, Equals, Raises, SourceEquals
from ..models import Assignment, Case, Question

_FORMATTED_Q3 = """
def A6Q3(a, b=1, c=5):
    ans1 = (-b + (b**2 - 4 * a * c) ** 0.5) / (2 * a)  # One root
    ans2 = (-b - (b**2 - 4 * a * c) ** 0.5) / (2 * a)  # The other root
    return (ans1, ans2)
"""

ASSIGNMENT = Assignment(
    id="A6",
    title="Assignment 6",
    questions=(
        Question(
            "Q1",
            "Slice a collection",
            (
                Case("Q1.1", args=([1, 2, 3, 4, 5], 1, -2), checks=(Equals([2, 3]),)),
                Case(
                    "Q1.2",
                    kwargs={"c": "abcdefghi", "start": -4, "stop": 2, "step": -1},
                    checks=(Equals("fed"),),
                ),
                Case("Q1.3", args=([1, 2, 3],), checks=(Equals([1, 2, 3]),)),
            ),
        ),
        Question(
            "Q2",
            "Find common and unique set elements",
            (
                Case(
                    "Q2.1",
                    args=([1, 2, 3], [2, 3, 4]),
                    checks=(Equals(({2, 3}, {1, 4})),),
                ),
                Case(
                    "Q2.2",
                    args=([1, 1, 2], [2, 3, 3]),
                    checks=(Equals(({2}, {1, 3})),),
                ),
            ),
        ),
        Question(
            "Q3",
            "Correct function formatting",
            (
                Case(
                    "Q3.1",
                    args=(1, -3, 2),
                    checks=(Approx((2, 1)), SourceEquals(_FORMATTED_Q3)),
                ),
            ),
        ),
        Question(
            "Q4",
            "Handle multiplication errors",
            (
                Case("Q4.1", args=(2, 5), checks=(Equals(10),)),
                Case("Q4.2", args=("ab", 3), checks=(Equals("ababab"),)),
                Case("Q4.3", args=("abcd", [1, 2, 3]), checks=(Equals(None),)),
            ),
        ),
        Question(
            "Q5",
            "Multiply one to four integers",
            (
                Case("Q5.1", args=(1, 2, 3), checks=(Equals(6),)),
                Case("Q5.2", args=(3, 3), checks=(Equals(9),)),
                Case("Q5.3", args=(2,), checks=(Equals(2),)),
                Case("Q5.4", args=(1, 2, 3, 4, 5), checks=(Raises(TypeError),)),
            ),
        ),
        Question(
            "Q6",
            "Add a structured docstring",
            (
                Case(
                    "Q6.1",
                    args=(3, 4),
                    checks=(
                        Approx(5),
                        DocstringContains(("Parameters", "Returns", "a : float")),
                    ),
                ),
            ),
        ),
    ),
)
