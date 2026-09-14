"""Public checks for Assignment 5."""

from __future__ import annotations

from ..checks import CsvEquals, Equals, LastLineIs, TextFileEquals
from ..models import Assignment, Case, Question, TextFixture

ASSIGNMENT = Assignment(
    id="A5",
    title="Assignment 5",
    fixtures=(
        TextFixture("file.txt", "this\nis\na\n\n\nfile"),
        TextFixture("data.csv", "x,y\n1,4\n2,5\n3,6"),
    ),
    questions=(
        Question(
            "Q1",
            "Count lines in a text file",
            (Case("Q1.1", args=("file.txt",), checks=(Equals(6),)),),
        ),
        Question(
            "Q2",
            "Count words in a text file",
            (Case("Q2.1", args=("file.txt",), checks=(Equals(4),)),),
        ),
        Question(
            "Q3",
            "Write repeated lines to a text file",
            (
                Case(
                    "Q3.1",
                    args=("output.txt", "line", 3),
                    checks=(
                        Equals(None),
                        TextFileEquals("output.txt", "line\nline\nline\n"),
                    ),
                ),
            ),
        ),
        Question(
            "Q4",
            "Write columnar data to a CSV file",
            (
                Case(
                    "Q4.1",
                    args=("output.csv", {"a": [9, 8, 7], "b": [6, 5, 4]}),
                    checks=(
                        Equals(None),
                        CsvEquals("output.csv", {"a": [9, 8, 7], "b": [6, 5, 4]}),
                    ),
                ),
            ),
        ),
        Question(
            "Q5",
            "Read a CSV file into a dictionary",
            (
                Case(
                    "Q5.1",
                    args=("data",),
                    checks=(Equals({"x": [1, 2, 3], "y": [4, 5, 6]}),),
                ),
            ),
        ),
        Question(
            "Q6",
            "Append a line to a text file",
            (
                Case(
                    "Q6.1",
                    args=("file.txt", "new line"),
                    checks=(Equals(None), LastLineIs("file.txt", "new line")),
                ),
            ),
        ),
    ),
)
