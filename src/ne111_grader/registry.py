"""Assignment specification registry."""

from __future__ import annotations

from .assignments.a1 import ASSIGNMENT
from .models import Assignment

_ASSIGNMENTS = {ASSIGNMENT.id: ASSIGNMENT}


def get_assignment(assignment_id: str) -> Assignment:
    normalized = assignment_id.upper()
    try:
        return _ASSIGNMENTS[normalized]
    except KeyError as error:
        available = ", ".join(sorted(_ASSIGNMENTS))
        raise KeyError(
            f"Unknown assignment {assignment_id!r}. Available: {available}"
        ) from error


def assignment_ids() -> tuple[str, ...]:
    return tuple(sorted(_ASSIGNMENTS))
