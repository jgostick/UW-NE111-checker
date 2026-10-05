"""Public checks for notebook-based Assignment 4."""

from __future__ import annotations

from ..checks import Equals, InsertedLetters, Raises, TypeIs
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
                Case("Q1.1", args=("abcEDEF111",), checks=(Equals(7), TypeIs(int))),
                Case("Q1.2", args=("abc EDEF111",), checks=(Equals(7), TypeIs(int))),
                Case("Q1.3", args=("abc EDEF111 **",), checks=(Equals(7), TypeIs(int))),
                Case("Q1.4", args=("Hello!",), checks=(Equals(5), TypeIs(int))),
                Case("Q1.5", args=("Room 204",), checks=(Equals(4), TypeIs(int))),
                Case("Q1.6", args=("123 !?",), checks=(Equals(0), TypeIs(int))),
                Case("Q1.7", args=("",), checks=(Equals(0), TypeIs(int))),
            ),
        ),
        Question(
            "Q2",
            "Count non-space characters",
            input_names=("value",),
            cases=(
                Case("Q2.1", args=("hello world",), checks=(Equals(10), TypeIs(int))),
                Case(
                    "Q2.2",
                    args=("Dear World, Hello!",),
                    checks=(Equals(16), TypeIs(int)),
                ),
                Case("Q2.3", args=(11,), checks=(Raises((AttributeError, TypeError)),)),
                Case(
                    "Q2.4", args=("Hi, world! 123",), checks=(Equals(12), TypeIs(int))
                ),
                Case("Q2.5", args=("a\tb",), checks=(Equals(3), TypeIs(int))),
                Case("Q2.6", args=("   ",), checks=(Equals(0), TypeIs(int))),
                Case("Q2.7", args=("",), checks=(Equals(0), TypeIs(int))),
                Case("Q2.8", args=(42,), checks=(Raises((TypeError, AttributeError)),)),
                Case("Q2.9", args=("a\nb",), checks=(Equals(3), TypeIs(int))),
                Case(
                    "Q2.10", args=(None,), checks=(Raises((TypeError, AttributeError)),)
                ),
            ),
        ),
        Question(
            "Q3",
            "Validate a password",
            input_names=("password",),
            cases=(
                Case("Q3.1", args=("password",), checks=(Equals(False), TypeIs(bool))),
                Case("Q3.2", args=("Passw0rd!",), checks=(Equals(True), TypeIs(bool))),
                Case("Q3.3", args=("River7!",), checks=(Equals(True), TypeIs(bool))),
                Case("Q3.4", args=("river7!",), checks=(Equals(False), TypeIs(bool))),
                Case("Q3.5", args=("RIVER7!",), checks=(Equals(False), TypeIs(bool))),
                Case("Q3.6", args=("River!",), checks=(Equals(False), TypeIs(bool))),
                Case("Q3.7", args=("River7",), checks=(Equals(False), TypeIs(bool))),
                Case("Q3.8", args=("River7?",), checks=(Equals(False), TypeIs(bool))),
                Case("Q3.9", args=("River7@",), checks=(Equals(True), TypeIs(bool))),
                Case("Q3.10", args=("River7#",), checks=(Equals(True), TypeIs(bool))),
                Case("Q3.11", args=("River7$",), checks=(Equals(True), TypeIs(bool))),
                Case("Q3.12", args=("River7%",), checks=(Equals(True), TypeIs(bool))),
                Case("Q3.13", args=("River7^",), checks=(Equals(True), TypeIs(bool))),
                Case("Q3.14", args=("River7&",), checks=(Equals(True), TypeIs(bool))),
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
                    checks=(Equals(False), TypeIs(bool)),
                ),
                Case(
                    "Q4.2",
                    args=("bob@gmail.com", "gmail.com"),
                    checks=(Equals(True), TypeIs(bool)),
                ),
                Case(
                    "Q4.3",
                    args=("alex@example.org", "example.org"),
                    checks=(Equals(True), TypeIs(bool)),
                ),
                Case(
                    "Q4.4",
                    args=("alex@example.org", "example.com"),
                    checks=(Equals(False), TypeIs(bool)),
                ),
                Case(
                    "Q4.5",
                    args=("alex@example.org.backup", "example.org"),
                    checks=(Equals(False), TypeIs(bool)),
                ),
                Case(
                    "Q4.6",
                    args=("alex@EXAMPLE.org", "example.org"),
                    checks=(Equals(False), TypeIs(bool)),
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
                    checks=(Equals(["test.csv"]), TypeIs(list)),
                ),
                Case(
                    "Q5.2",
                    args=(["file1.txt", "test.csv", "blob.csv"], "csv"),
                    checks=(Equals(["test.csv", "blob.csv"]), TypeIs(list)),
                ),
                Case(
                    "Q5.3",
                    args=(["file1.txt", "test.csv", "blob.csv"], "py"),
                    checks=(Equals([]), TypeIs(list)),
                ),
                Case(
                    "Q5.4",
                    args=(["notes.txt", "results.csv", "backup.csv"], "csv"),
                    checks=(Equals(["results.csv", "backup.csv"]), TypeIs(list)),
                ),
                Case(
                    "Q5.5",
                    args=(["notes.txt", "results.csv"], "png"),
                    checks=(Equals([]), TypeIs(list)),
                ),
                Case(
                    "Q5.6",
                    args=(["results.csv.bak", "results.csv"], "csv"),
                    checks=(Equals(["results.csv"]), TypeIs(list)),
                ),
                Case("Q5.7", args=([], "txt"), checks=(Equals([]), TypeIs(list))),
                Case(
                    "Q5.8",
                    args=(["results.CSV", "resultscsv", "results.csv"], "csv"),
                    checks=(Equals(["results.csv"]), TypeIs(list)),
                ),
            ),
        ),
        Question(
            "Q6",
            "Compare two strings",
            input_names=("a", "b"),
            cases=(
                Case("Q6.1", args=("a", "b"), checks=(Equals(True), TypeIs(bool))),
                Case("Q6.2", args=("c", "b"), checks=(Equals(False), TypeIs(bool))),
                Case(
                    "Q6.3",
                    args=("apple", "banana"),
                    checks=(Equals(True), TypeIs(bool)),
                ),
                Case(
                    "Q6.4", args=("pear", "apple"), checks=(Equals(False), TypeIs(bool))
                ),
                Case(
                    "Q6.5", args=("same", "same"), checks=(Equals(False), TypeIs(bool))
                ),
                Case(
                    "Q6.6", args=("cat", "catalog"), checks=(Equals(True), TypeIs(bool))
                ),
                Case(
                    "Q6.7", args=("Apple", "apple"), checks=(Equals(True), TypeIs(bool))
                ),
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
                    checks=(Equals("onetwothree"), TypeIs(str)),
                ),
                Case(
                    "Q7.2",
                    args=(["foo", " ", "bar"],),
                    checks=(Equals("foo bar"), TypeIs(str)),
                ),
                Case("Q7.3", args=(["foo", [], "bar"],), checks=(Raises(TypeError),)),
                Case(
                    "Q7.4",
                    args=(["Hello", " ", "world!"],),
                    checks=(Equals("Hello world!"), TypeIs(str)),
                ),
                Case(
                    "Q7.5",
                    args=(["red", "blue"],),
                    checks=(Equals("redblue"), TypeIs(str)),
                ),
                Case("Q7.6", args=([],), checks=(Equals(""), TypeIs(str))),
                Case("Q7.7", args=(["Room ", 204],), checks=(Raises(TypeError),)),
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
                    checks=(Equals({"key1": "value2", "key2": "value2"}), TypeIs(dict)),
                ),
                Case(
                    "Q8.2",
                    args=("key1:value2,key2:value2",),
                    checks=(Raises(ValueError),),
                ),
                Case(
                    "Q8.3",
                    args=("name:Alex;course:NE111",),
                    checks=(Equals({"name": "Alex", "course": "NE111"}), TypeIs(dict)),
                ),
                Case(
                    "Q8.4",
                    args=("count:12",),
                    checks=(Equals({"count": "12"}), TypeIs(dict)),
                ),
                Case(
                    "Q8.5",
                    args=("name=Alex;course:NE111",),
                    checks=(Raises(ValueError),),
                ),
                Case(
                    "Q8.6",
                    args=("name:Alex,course:NE111",),
                    checks=(Raises(ValueError),),
                ),
                Case("Q8.7", args=("name:Alex:extra",), checks=(Raises(ValueError),)),
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
                    checks=(InsertedLetters("test", 2),),
                ),
                Case(
                    "Q9.2",
                    args=("tABeCDsEFtGG", 2, "decrypt"),
                    checks=(Equals("test"), TypeIs(str)),
                ),
                Case(
                    "Q9.3",
                    args=("Hi", 2, "encrypt"),
                    checks=(InsertedLetters("Hi", 2),),
                ),
                Case(
                    "Q9.4",
                    args=("HabixY", 2, "decrypt"),
                    checks=(Equals("Hi"), TypeIs(str)),
                ),
                Case(
                    "Q9.5",
                    args=("go", 0, "encrypt"),
                    checks=(InsertedLetters("go", 0),),
                ),
                Case("Q9.6", args=("", 2, "encrypt"), checks=(InsertedLetters("", 2),)),
                Case(
                    "Q9.7",
                    args=("go", 0, "decrypt"),
                    checks=(Equals("go"), TypeIs(str)),
                ),
                Case("Q9.8", args=("", 2, "decrypt"), checks=(Equals(""), TypeIs(str))),
                Case(
                    "Q9.9",
                    args=("Hi", 1, "encrypt"),
                    checks=(InsertedLetters("Hi", 1),),
                ),
                Case(
                    "Q9.10",
                    args=("Haib", 1, "decrypt"),
                    checks=(Equals("Hi"), TypeIs(str)),
                ),
            ),
        ),
    ),
)
