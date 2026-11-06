"""Public checks for Assignment 7."""

from __future__ import annotations

import ast

import numpy as np

from ..checks import Approx, AvoidsSyntax, DTypeIs, Equals, ItemAt, TypeIs, UsesSyntax
from ..models import Assignment, Case, Question

ASSIGNMENT = Assignment(
    id="A7",
    title="Assignment 7",
    questions=(
        Question(
            "Q1",
            "Convert an array to integers",
            (
                Case(
                    "Q1.1",
                    args=(np.array([2.2, 4.8, 0.9, 3.0]),),
                    checks=(
                        Equals(np.array([2, 4, 0, 3])),
                        TypeIs(np.ndarray),
                        DTypeIs(int),
                    ),
                ),
                Case(
                    "Q1.2",
                    args=(np.array([[-2.8, 0.9], [3.0, -0.9]]),),
                    checks=(
                        Equals(np.array([[-2, 0], [3, 0]])),
                        TypeIs(np.ndarray),
                        DTypeIs(int),
                    ),
                ),
            ),
        ),
        Question(
            "Q2",
            "Compute sphere volumes and surface areas",
            (
                Case(
                    "Q2.1",
                    args=([4.4, 3.2, 8.3],),
                    checks=(
                        Approx(
                            np.array(
                                [
                                    [356.8179048, 243.28493509],
                                    [137.25827743, 128.67963509],
                                    [2395.09578482, 865.69727162],
                                ]
                            )
                        ),
                        TypeIs(np.ndarray),
                    ),
                ),
            ),
        ),
        Question(
            "Q3",
            "Split a two-dimensional array",
            (
                Case(
                    "Q3.1",
                    args=(np.array([[0, 1, 2, 6, 7], [3, 4, 5, 8, 9]]), (1, 3)),
                    checks=(
                        Equals(
                            [
                                [np.array([[0, 1, 2]]), np.array([[6, 7]])],
                                [np.array([[3, 4, 5]]), np.array([[8, 9]])],
                            ]
                        ),
                        TypeIs(list),
                        ItemAt(0, TypeIs(list)),
                        ItemAt(1, TypeIs(list)),
                        ItemAt(0, ItemAt(0, TypeIs(np.ndarray))),
                        ItemAt(0, ItemAt(1, TypeIs(np.ndarray))),
                        ItemAt(1, ItemAt(0, TypeIs(np.ndarray))),
                        ItemAt(1, ItemAt(1, TypeIs(np.ndarray))),
                        UsesSyntax(ast.Slice, "slice notation"),
                    ),
                ),
            ),
        ),
        Question(
            "Q4",
            "Count values relative to a threshold",
            (
                Case(
                    "Q4.1",
                    args=([[4, 6, 2], [5, 4, 7]], 5),
                    checks=(
                        Equals((3, 1, 2)),
                        TypeIs(tuple),
                        AvoidsSyntax(ast.For, "a for loop"),
                    ),
                ),
            ),
        ),
        Question(
            "Q5",
            "Normalize an array",
            (
                Case(
                    "Q5.1",
                    args=([[1, 4, -2], [-2, 0, 1]],),
                    checks=(
                        Approx(np.array([[0.5, 1.0, 0.0], [0.0, 1.0 / 3.0, 0.5]])),
                        TypeIs(np.ndarray),
                    ),
                ),
            ),
        ),
        Question(
            "Q6",
            "Find column maxima and minima",
            (
                Case(
                    "Q6.1",
                    args=(
                        np.array(
                            [[3, 5, 2, 4], [2, 6, 1, 5], [2, 4, 4, 8], [1, 1, 5, 3]]
                        ),
                    ),
                    checks=(
                        Equals(np.array([[3, 6, 5, 8], [1, 1, 1, 3]])),
                        TypeIs(np.ndarray),
                    ),
                ),
            ),
        ),
        Question(
            "Q7",
            "Stack arrays when exactly one direction is feasible",
            (
                Case(
                    "Q7.1",
                    args=(np.array([1, 2, 3]), np.array([[4, 5, 6], [7, 8, 9]])),
                    checks=(
                        Equals(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),
                        TypeIs(np.ndarray),
                    ),
                ),
                Case(
                    "Q7.2",
                    args=([1, 2, 3], [4, 5]),
                    checks=(Equals(np.array([1, 2, 3, 4, 5])), TypeIs(np.ndarray)),
                ),
                Case(
                    "Q7.3",
                    args=([1, 2], [4, 5]),
                    checks=(Equals(None),),
                ),
                Case(
                    "Q7.4",
                    args=(np.ones((2, 3)), np.ones((3, 2))),
                    checks=(Equals(None),),
                ),
            ),
        ),
        Question(
            "Q8",
            "Sum even array values",
            (
                Case(
                    "Q8.1",
                    args=(np.array([[4, 3, 7], [2, 6, 9], [0, -2, 1]]),),
                    checks=(Equals(10), AvoidsSyntax(ast.For, "a for loop")),
                ),
            ),
        ),
    ),
)
