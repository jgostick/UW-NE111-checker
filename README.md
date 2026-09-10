# UW NE 111 Grader

Prototype of a reusable grading engine and student-facing Streamlit app for
UW NE 111 assignments.

## Student workflow

After the package is released, create the course environment once:

```console
conda create -n ne111 python=3.12 pip -y
conda activate ne111
python -m pip install uw-ne111-grader==0.1.0
```

For each work session, activate the environment, change to the folder containing
the submission, and select the assignment:

```console
conda activate ne111
cd path/to/assignment
ne111-grader A1
```

The current prototype expects `A1.py` in the working directory. An explicit
path can also be supplied:

```console
ne111-grader A1 --submission path/to/A1.py
```

Stop the Streamlit server with `Ctrl+C`.

## Development

Create a local environment from the repository:

```console
conda env create --file environment.yml
conda activate ne111
pytest
ne111-grader A1 --submission path/to/A1.py
```

Alternatively, with uv:

```console
uv run --extra dev pytest
uv run ne111-grader A1 --submission path/to/A1.py
```

## Architecture

- `models.py` defines assignments, questions, cases, and structured results.
- `checks.py` contains composable checks such as exact equality, approximate
  equality, expected exceptions, and silence.
- `runner.py` is a pure in-process executor with no Streamlit dependency.
- `worker.py` loads and tests a submission in a temporary working directory.
- `isolated.py` manages child processes and enforces timeouts.
- `student_app.py` renders any registered assignment specification.
- `assignments/` contains public test specifications.

The child process protects the Streamlit app from ordinary crashes, import
failures, and infinite loops. It is not a security sandbox: deliberately hostile
submissions require operating-system or container isolation.

Private marker cases should live outside this public package. A future marker
dashboard can consume the same result model while loading a separate private
specification package.
