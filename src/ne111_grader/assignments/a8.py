"""Public checks for Assignment 8."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from ..checks import (
    Attribute,
    Equals,
    ItemAt,
    LengthIs,
    MaxIs,
    MethodResult,
    MinIs,
    TypeIs,
)
from ..models import Assignment, Case, Question

_HISTOGRAM_DATA = tuple(np.linspace(index, index + 1, 10) for index in range(3))
_FILTER_X = np.array([-1.0, 0.1, 0.2, 0.5, 2.0])
_FILTER_Y = np.array([0.2, 0.2, 0.8, 1.0, 0.4])

ASSIGNMENT = Assignment(
    id="A8",
    title="Assignment 8",
    questions=(
        Question(
            "Q1",
            "Generate a scatter plot",
            (
                Case(
                    "Q1.1",
                    args=([1, 1], [4, 4]),
                    checks=(TypeIs(tuple),),
                ),
                Case(
                    "Q1.2",
                    args=([1, 2, 3], [4, 5, 6]),
                    checks=(LengthIs(2),),
                ),
                Case(
                    "Q1.3",
                    args=([0, 0, 0], [0, 0, 2]),
                    checks=(ItemAt(0, TypeIs(plt.Figure)),),
                ),
                Case(
                    "Q1.4",
                    args=([0, 0, 0], [0, 0, 2]),
                    checks=(ItemAt(1, TypeIs(plt.Axes)),),
                ),
            ),
        ),
        Question(
            "Q2",
            "Generate a row of histogram subplots",
            (
                Case(
                    "Q2.1",
                    args=_HISTOGRAM_DATA,
                    checks=(ItemAt(1, LengthIs(3)),),
                ),
            ),
        ),
        Question(
            "Q3",
            "Plot an image",
            (
                Case(
                    "Q3.1",
                    args=(np.arange(100).reshape((10, 10)),),
                    checks=(ItemAt(1, Attribute("images", LengthIs(1))),),
                ),
            ),
        ),
        Question(
            "Q4",
            "Set a figure background color",
            (
                Case(
                    "Q4.1",
                    args=(plt.Figure(), "k"),
                    checks=(MethodResult("get_facecolor", Equals((0.0, 0.0, 0.0, 1))),),
                ),
            ),
        ),
        Question(
            "Q5",
            "Filter data before plotting",
            (
                Case(
                    "Q5.1",
                    args=(_FILTER_X, _FILTER_Y),
                    checks=(ItemAt(1, Attribute("dataLim", MinIs(0.1))),),
                ),
                Case(
                    "Q5.2",
                    args=(_FILTER_X, _FILTER_Y),
                    checks=(ItemAt(1, Attribute("dataLim", MaxIs(1.0))),),
                ),
            ),
        ),
    ),
)
