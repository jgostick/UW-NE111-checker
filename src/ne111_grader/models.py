"""Data structures shared by assignment specifications and grader interfaces."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "message": self.message}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> CheckResult:
        return cls(passed=bool(value["passed"]), message=str(value["message"]))


@dataclass(frozen=True)
class CallRecord:
    return_value: Any = None
    exception: BaseException | None = None
    stdout: str = ""
    stderr: str = ""
    source: str = ""


class Check(Protocol):
    """A composable assertion evaluated against one function call."""

    def evaluate(self, record: CallRecord) -> CheckResult: ...


@dataclass(frozen=True)
class Case:
    id: str
    args: tuple[Any, ...] = ()
    kwargs: Mapping[str, Any] = field(default_factory=dict)
    checks: tuple[Check, ...] = ()
    description: str = ""


@dataclass(frozen=True)
class Question:
    id: str
    title: str
    cases: tuple[Case, ...]


@dataclass(frozen=True)
class TextFixture:
    path: str
    contents: str


@dataclass(frozen=True)
class Assignment:
    id: str
    title: str
    questions: tuple[Question, ...]
    fixtures: tuple[TextFixture, ...] = ()

    @property
    def expected_filename(self) -> str:
        return f"{self.id}.py"

    def question(self, question_id: str) -> Question:
        for question in self.questions:
            if question.id == question_id:
                return question
        raise KeyError(f"Unknown question {question_id!r} for {self.id}")


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    passed: bool
    checks: tuple[CheckResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "checks": [check.to_dict() for check in self.checks],
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> CaseResult:
        checks = tuple(CheckResult.from_dict(item) for item in value["checks"])
        return cls(
            case_id=str(value["case_id"]),
            passed=bool(value["passed"]),
            checks=checks,
        )


@dataclass(frozen=True)
class QuestionResult:
    assignment_id: str
    question_id: str
    cases: tuple[CaseResult, ...]

    @property
    def passed(self) -> bool:
        return bool(self.cases) and all(case.passed for case in self.cases)

    def to_dict(self) -> dict[str, Any]:
        return {
            "assignment_id": self.assignment_id,
            "question_id": self.question_id,
            "passed": self.passed,
            "cases": [case.to_dict() for case in self.cases],
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> QuestionResult:
        return cls(
            assignment_id=str(value["assignment_id"]),
            question_id=str(value["question_id"]),
            cases=tuple(CaseResult.from_dict(item) for item in value["cases"]),
        )


def resolve_submission(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()
