# UW-NE111-checker agent guide

## Scope and privacy

- This is the public, student-facing `uw-ne111-checker` Python package. It provides the `ne111-checker` command and reusable Streamlit checker.
- Everything committed here must be safe for students to inspect. Include only public checks and actionable feedback justified by the handout. Never expose reference solutions, hidden cases or inputs, undisclosed expected values, grading thresholds, gradebook settings, or marker-only logic.
- `UW-NE111` owns authoritative assignment requirements. The private sibling `UW-NE111-marker` may depend on this package; this package must never depend on or copy code from the marker.

## Architecture

- `src/ne111_checker/assignments/a<N>.py`: public `Assignment`/`Question`/`Case` specifications.
- `src/ne111_checker/models.py` and `checks.py`: shared immutable result/specification models and composable checks.
- `registry.py`: assignment registration; update it when adding an assignment.
- `runner.py`: in-process execution; `worker.py` and `isolated.py`: temporary-directory/process execution and timeouts.
- `cli.py` (`ne111-checker`) and `student_app.py`: command-line and Streamlit entry points.
- `tests/`: runner, syntax-check, UI, and per-assignment integration coverage.

## Setup and exact verification

- Python support is 3.10 through 3.12. See `README.md` for student installation and CLI usage.
- Conda development: `conda env create --file environment.yml`, `conda activate ne111`, then `pytest`.
- uv development/test command: `uv run --extra dev pytest`.
- Before handoff, also run `uv run --extra dev ruff check .` and `uv run --extra dev ruff format --check .`.
- Smoke-test an edited assignment through the real entry point when relevant: `uv run ne111-checker A1 --submission path/to/A1.py` (replace `A1` and the path).

## Code and test conventions

- Use the `src/` package layout, `from __future__ import annotations`, type annotations, relative intra-package imports, and focused module docstrings. Follow Ruff's default formatting.
- Keep execution/result logic independent of Streamlit; UI code consumes structured results from the runner/isolated layers.
- Model specifications with immutable dataclasses and tuples. Give stable IDs to assignments (`A1`), questions (`Q1`), and cases (`Q1.1`).
- Add deterministic pytest coverage for public cases and user-visible failures. Use `tmp_path` for submission/filesystem tests and Streamlit `AppTest` for UI behaviour.
- The child-process boundary handles ordinary faulty submissions, not hostile code; do not describe it as a security sandbox.

## Assignment and cross-repository changes

1. Confirm the requirement in the matching `UW-NE111/content/<chapter>/A<N>/A<N>_questions.qmd`; do not infer new requirements from old checker code.
2. Add/update the public assignment module and registration, keeping titles, IDs, signatures, syntax rules, and required side effects aligned with the handout.
3. Choose illustrative student-visible cases and feedback only. A public check must not reveal the private case set or marking policy.
4. Add/update integration tests, run this repository's checks, then update private cases and gradebook details in `UW-NE111-marker` and run its tests separately.
5. Put reusable checks, execution machinery, and result models here when they are safe to publish; keep marker dashboards, batch reports, hidden cases, thresholds, and marking rationale private.

## Git discipline

- Treat `UW-NE111`, this folder, and `UW-NE111-marker` as independent Git repositories. Check status and diffs separately.
- Never commit or push unless explicitly requested. Never include files from another repository in this repository's commit.
- Preserve unrelated user changes. Do not commit build artifacts, virtual environments, caches, or student submissions.
