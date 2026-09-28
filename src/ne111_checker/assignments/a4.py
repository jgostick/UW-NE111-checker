"""Public checks for notebook-based Assignment 4."""

from __future__ import annotations

from ..checks import Equals, LengthIs, Raises, TypeIs
from ..models import Assignment, Case, Question

ASSIGNMENT = Assignment(
    id="A4",
    title="Assignment 4",
    notebook_submission=True,
    questions=(
        Question(
            "Q1",
            "Count letters in a string",
            input_names=("value",),
            cases=(
                Case("Q1.1", args=("abcEDEF111",), checks=(Equals(7),)),
                Case("Q1.2", args=("abc EDEF111",), checks=(Equals(7),)),
                Case("Q1.3", args=("abc EDEF111 **",), checks=(Equals(7),)),
            ),
        ),
        Question(
            "Q2",
            "Count non-space characters",
            input_names=("value",),
            cases=(
                Case("Q2.1", args=("hello world",), checks=(Equals(10),)),
                Case("Q2.2", args=("Dear World, Hello!",), checks=(Equals(16),)),
                Case("Q2.3", args=(11,), checks=(Raises((AttributeError, TypeError)),)),
            ),
        ),
        Question(
            "Q3",
            "Validate a password",
            input_names=("password",),
            cases=(
                Case("Q3.1", args=("password",), checks=(Equals(False),)),
                Case("Q3.2", args=("Passw0rd!",), checks=(Equals(True),)),
            ),
        ),
        Question(
            "Q4",
            "Check an email domain",
            input_names=("email", "domain"),
            cases=(
                Case(
                    "Q4.1",
                    args=("bob@gmail.com", "hotmail.com"),
                    checks=(Equals(False),),
                ),
                Case(
                    "Q4.2",
                    args=("bob@gmail.com", "gmail.com"),
                    checks=(Equals(True),),
                ),
            ),
        ),
        Question(
            "Q5",
            "Filter filenames by extension",
            input_names=("filenames", "extension"),
            cases=(
                Case(
                    "Q5.1",
                    args=(["file1.txt", "test.csv"], "csv"),
                    checks=(Equals(["test.csv"]),),
                ),
                Case(
                    "Q5.2",
                    args=(["file1.txt", "test.csv", "blob.csv"], "csv"),
                    checks=(Equals(["test.csv", "blob.csv"]),),
                ),
                Case(
                    "Q5.3",
                    args=(["file1.txt", "test.csv", "blob.csv"], "py"),
                    checks=(Equals([]),),
                ),
            ),
        ),
        Question(
            "Q6",
            "Compare two strings",
            input_names=("a", "b"),
            cases=(
                Case("Q6.1", args=("a", "b"), checks=(Equals(True),)),
                Case("Q6.2", args=("c", "b"), checks=(Equals(False),)),
            ),
        ),
        Question(
            "Q7",
            "Join a list of strings",
            input_names=("values",),
            cases=(
                Case(
                    "Q7.1",
                    args=(["one", "two", "three"],),
                    checks=(Equals("onetwothree"),),
                ),
                Case(
                    "Q7.2",
                    args=(["foo", " ", "bar"],),
                    checks=(Equals("foo bar"),),
                ),
                Case(
                    "Q7.3",
                    args=(["foo", [], "bar"],),
                    checks=(Raises(TypeError),),
                ),
            ),
        ),
        Question(
            "Q8",
            "Convert key-value text to a dictionary",
            input_names=("value",),
            cases=(
                Case(
                    "Q8.1",
                    args=("key1:value2;key2:value2",),
                    checks=(Equals({"key1": "value2", "key2": "value2"}),),
                ),
                Case(
                    "Q8.2",
                    args=("key1:value2,key2:value2",),
                    checks=(Raises(ValueError),),
                ),
            ),
        ),
        Question(
            "Q9",
            "Encrypt and decrypt messages",
            input_names=("message", "number", "mode"),
            cases=(
                Case(
                    "Q9.1",
                    args=("test", 2, "encrypt"),
                    checks=(LengthIs(12), TypeIs(str)),
                ),
                Case(
                    "Q9.2",
                    args=("tABeCDsEFtGG", 2, "decrypt"),
                    checks=(Equals("test"),),
                ),
            ),
        ),
    ),
)
