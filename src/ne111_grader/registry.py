"""Assignment specification registry."""

from __future__ import annotations

from .assignments.a1 import ASSIGNMENT as A1
from .assignments.a2 import ASSIGNMENT as A2
from .assignments.a3 import ASSIGNMENT as A3
from .assignments.a4 import ASSIGNMENT as A4
from .assignments.a5 import ASSIGNMENT as A5
from .assignments.a6 import ASSIGNMENT as A6
from .assignments.a7 import ASSIGNMENT as A7
from .assignments.a8 import ASSIGNMENT as A8
from .models import Assignment

_ASSIGNMENTS = {
    assignment.id: assignment for assignment in (A1, A2, A3, A4, A5, A6, A7, A8)
}


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
