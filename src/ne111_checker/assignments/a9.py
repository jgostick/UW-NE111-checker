"""Public checks for Assignment 9."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.colors import to_rgba
from matplotlib.container import BarContainer
from matplotlib.figure import Figure
from matplotlib.image import AxesImage

from ..checks import Approx, Attribute, Equals, ItemAt, LengthIs, MethodResult, TypeIs
from ..models import Assignment, CallRecord, Case, Check, CheckResult, Question


@dataclass(frozen=True)
class _PlotHandles:
    """Check that the returned Axes belong to the returned figure."""

    count: int = 1

    def evaluate(self, record: CallRecord) -> CheckResult:
        if record.exception is not None:
            error = record.exception
            return CheckResult(False, f"Raised {type(error).__name__}: {error}")
        result = record.return_value
        if not isinstance(result, tuple) or len(result) != 2:
            return CheckResult(False, "Return a tuple containing the figure and Axes.")
        figure, axes = result
        if not isinstance(figure, Figure):
            return CheckResult(False, "Return a Matplotlib Figure as the first item.")
        if self.count == 1:
            passed = isinstance(axes, Axes) and axes in figure.axes
        else:
            try:
                passed = len(axes) == self.count and all(
                    isinstance(ax, Axes) and ax in figure.axes for ax in axes
                )
                passed = passed and len(figure.axes) == self.count
            except TypeError:
                passed = False
        if not passed:
            return CheckResult(False, "Return the Axes from the figure you created.")
        return CheckResult(True, "Returned the figure and its Axes.")


def _scatter_checks(x: np.ndarray, y: np.ndarray) -> tuple[Check, ...]:
    return (
        _PlotHandles(),
        ItemAt(1, Attribute("collections", LengthIs(1))),
        ItemAt(1, Attribute("collections", ItemAt(0, TypeIs(PathCollection)))),
        ItemAt(
            1,
            Attribute(
                "collections",
                ItemAt(0, MethodResult("get_offsets", Approx(np.column_stack((x, y))))),
            ),
        ),
    )


def _histogram_checks(arrays: tuple[np.ndarray, ...]) -> tuple[Check, ...]:
    count = len(arrays)
    checks: list[Check] = [_PlotHandles(count)]
    for index, array in enumerate(arrays):
        subplot = MethodResult("get_geometry", Equals((1, count, index, index)))
        checks.append(
            ItemAt(1, ItemAt(index, MethodResult("get_subplotspec", subplot)))
        )
        bars = (
            LengthIs(1),
            ItemAt(0, TypeIs(BarContainer)),
            ItemAt(0, Attribute("orientation", Equals("vertical"))),
            ItemAt(0, Attribute("datavalues", Equals(np.histogram(array)[0]))),
        )
        checks.extend(
            ItemAt(1, ItemAt(index, Attribute("containers", bar))) for bar in bars
        )
    return tuple(checks)


_X = np.array([0.0, 1.0, 2.0])
_Y = np.array([1.5, 0.0, 3.0])
_HISTOGRAMS = (
    np.array([0, 1, 1, 2]),
    np.array([2, 3, 3, 4, 4]),
    np.array([5, 6, 8]),
)
_IMAGE = np.arange(6).reshape(2, 3)
_FIGURE = Figure(label="Temperature readings")
_FIGURE.add_subplot().set_title("Test run")
_FILTER_X = np.array([-0.2, 0.0, 0.4, 0.7, 1.0])
_FILTER_Y = np.array([0.5, 1.0, 1.2, 0.3, 0.0])

ASSIGNMENT = Assignment(
    id="A9",
    title="Assignment 9",
    questions=(
        Question(
            "Q1",
            "Generate a scatter plot",
            (Case("Q1.1", args=(_X, _Y), checks=_scatter_checks(_X, _Y)),),
        ),
        Question(
            "Q2",
            "Generate a row of histogram subplots",
            (Case("Q2.1", args=_HISTOGRAMS, checks=_histogram_checks(_HISTOGRAMS)),),
        ),
        Question(
            "Q3",
            "Plot an image",
            (
                Case(
                    "Q3.1",
                    args=(_IMAGE,),
                    checks=(
                        _PlotHandles(),
                        ItemAt(1, Attribute("images", LengthIs(1))),
                        ItemAt(1, Attribute("images", ItemAt(0, TypeIs(AxesImage)))),
                        ItemAt(
                            1,
                            Attribute(
                                "images",
                                ItemAt(0, MethodResult("get_array", Equals(_IMAGE))),
                            ),
                        ),
                    ),
                ),
            ),
        ),
        Question(
            "Q4",
            "Set a figure background color",
            (
                Case(
                    "Q4.1",
                    kwargs={"fig": _FIGURE, "color": "grey"},
                    checks=(
                        TypeIs(Figure),
                        MethodResult("get_label", Equals("Temperature readings")),
                        Attribute("axes", LengthIs(1)),
                        Attribute(
                            "axes",
                            ItemAt(0, MethodResult("get_title", Equals("Test run"))),
                        ),
                        MethodResult("get_facecolor", Approx(to_rgba("grey"))),
                    ),
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
                    checks=_scatter_checks(_FILTER_X[[1, 3, 4]], _FILTER_Y[[1, 3, 4]]),
                ),
            ),
        ),
    ),
)
