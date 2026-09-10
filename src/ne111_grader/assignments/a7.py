"""Public checks for Assignment 7."""

from __future__ import annotations

import ast

import numpy as np

from ..checks import Approx, AvoidsCall, AvoidsSyntax, Equals, UsesSymbol
from ..models import Assignment, Case, Question

ASSIGNMENT = Assignment(
    id="A7",
    title="Assignment 7",
    questions=(
        Question(
            "Q1",
            "Check whether arrays can broadcast",
            (
                Case(
                    "Q1.1",
                    args=(np.ones((3, 3)), np.ones((1, 3))),
                    checks=(Equals(True),),
                ),
                Case(
                    "Q1.2",
                    args=(np.ones((3, 3)), np.ones((1, 4))),
                    checks=(Equals(False),),
                ),
                Case("Q1.3", args=(1.0, np.ones((1, 4))), checks=(Equals(True),)),
                Case(
                    "Q1.4",
                    args=(np.ones((3, 3)), np.ones((4,))),
                    checks=(Equals(False),),
                ),
            ),
        ),
        Question(
            "Q2",
            "Apply a NumPy universal function",
            (
                Case(
                    "Q2.1",
                    args=(np.arange(4), np.arange(4, 8), "+"),
                    checks=(Equals(np.array([4, 6, 8, 10])),),
                ),
                Case(
                    "Q2.2",
                    args=(np.arange(4), np.arange(4, 8), "*"),
                    checks=(Equals(np.array([0, 5, 12, 21])),),
                ),
                Case(
                    "Q2.3",
                    args=(np.arange(4), np.arange(4, 8), "//"),
                    checks=(
                        Equals(np.array([0, 0, 0, 0])),
                        UsesSymbol("floor_divide"),
                    ),
                ),
            ),
        ),
        Question(
            "Q3",
            "Find a two-dimensional bounding box",
            (
                Case(
                    "Q3.1",
                    args=(np.array([[0.3, 0.2], [0.8, 0.3], [0.4, 0.7], [0.2, 0.5]]),),
                    checks=(Approx(((0.2, 0.2), (0.8, 0.7))),),
                ),
            ),
        ),
        Question(
            "Q4",
            "Normalize a vector",
            (
                Case(
                    "Q4.1",
                    args=([4.1, 3.3, 5.0, -2.0],),
                    checks=(
                        Approx(
                            np.array([0.544493, 0.43825, 0.664016, -0.265606]),
                            rtol=1e-5,
                        ),
                    ),
                ),
            ),
        ),
        Question(
            "Q5",
            "Multiply a matrix and vector",
            (
                Case(
                    "Q5.1",
                    args=(np.arange(16).reshape((4, 4)), np.arange(100, 104)),
                    checks=(Equals(np.array([614, 2238, 3862, 5486])),),
                ),
                Case(
                    "Q5.2",
                    args=(
                        np.arange(16).reshape((4, 4)),
                        np.arange(100, 104).reshape((4, 1)),
                    ),
                    checks=(Equals(np.array([614, 2238, 3862, 5486])),),
                ),
            ),
        ),
        Question(
            "Q6",
            "Compute a matrix trace with boolean indexing",
            (
                Case(
                    "Q6.1",
                    args=(np.arange(16).reshape((4, 4)),),
                    checks=(Equals(30),),
                ),
                Case(
                    "Q6.2",
                    args=(np.arange(16).reshape((4, 4)),),
                    checks=(
                        AvoidsCall("trace"),
                        AvoidsSyntax(ast.For, "a for loop"),
                    ),
                ),
            ),
        ),
        Question(
            "Q7",
            "Identify a triangular matrix",
            (
                Case(
                    "Q7.1",
                    args=(
                        np.array(
                            [[1, 2, 3, 4], [0, 2, 3, 4], [0, 0, 3, 4], [0, 0, 0, 4]]
                        ),
                    ),
                    checks=(Equals(True),),
                ),
                Case(
                    "Q7.2",
                    args=(
                        np.array(
                            [[1, 2, 3, 4], [3, 2, 3, 4], [3, 0, 3, 4], [1, 0, 1, 4]]
                        ),
                    ),
                    checks=(Equals(False),),
                ),
            ),
        ),
    ),
)
