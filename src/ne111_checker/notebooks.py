"""Read the small, deliberate notebook submission format used by the checker."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

_TAG = re.compile(r"^\s*#\s*(?P<tag>setup|A\d+Q\d+)\s*$", re.IGNORECASE)


class NotebookFormatError(ValueError):
    """A notebook cannot be evaluated using the NE111 submission convention."""


@dataclass(frozen=True)
class Notebook:
    """Code sources grouped by their explicit NE111 cell tag."""

    setup_sources: tuple[str, ...]
    answers: dict[str, str]

    def answer_for(self, tag: str) -> str:
        try:
            return self.answers[tag.upper()]
        except KeyError as error:
            raise NotebookFormatError(
                f"No code cell is tagged # {tag.upper()}"
            ) from error


def _source(cell: object) -> str:
    if not isinstance(cell, dict):
        raise NotebookFormatError("Notebook cells must be JSON objects")
    source = cell.get("source", "")
    if isinstance(source, str):
        return source
    if isinstance(source, list) and all(isinstance(line, str) for line in source):
        return "".join(source)
    raise NotebookFormatError("A code cell has an invalid source")


def _tag(source: str) -> str | None:
    for line in source.splitlines():
        if not line.strip():
            continue
        match = _TAG.fullmatch(line)
        return match.group("tag").upper() if match else None
    return None


def load_notebook(path: Path) -> Notebook:
    """Load tagged code cells without executing notebook outputs or metadata."""
    try:
        contents = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise NotebookFormatError(f"Could not read notebook: {error}") from error

    if not isinstance(contents, dict) or not isinstance(contents.get("cells"), list):
        raise NotebookFormatError("This is not a valid Jupyter notebook")

    setup_sources: list[str] = []
    answers: dict[str, str] = {}
    for cell in contents["cells"]:
        if not isinstance(cell, dict) or cell.get("cell_type") != "code":
            continue
        source = _source(cell)
        tag = _tag(source)
        if tag == "SETUP":
            setup_sources.append(source)
        elif tag is not None:
            if tag in answers:
                raise NotebookFormatError(f"More than one code cell is tagged # {tag}")
            answers[tag] = source

    return Notebook(tuple(setup_sources), answers)
