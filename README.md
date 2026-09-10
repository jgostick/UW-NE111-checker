# UW NE 111 Grader

Reusable grading engine and student-facing Streamlit app for UW NE 111
assignments.

## Student installation

Do this once in Anaconda Prompt on Windows or a terminal on macOS:

```console
conda create -n ne111 python=3.12 pip git -y
conda activate ne111
python -m pip install "uw-ne111-grader @ git+https://github.com/jgostick/UW-NE111-grader.git@main"
```

## Using the grader

For each work session, activate the environment and launch the required
assignment (`A1` through `A8`):

```console
conda activate ne111
ne111-grader A3
```

The grader opens in a browser. Browse for your `.py` file, select a question tab,
and press its **Run** button. The filename itself does not matter.

If the file is named `A3.py` and the command is run from the same directory, it
is selected automatically. A path can also be supplied explicitly:

```console
ne111-grader A3 --submission path/to/A3.py
```

Stop the Streamlit server with `Ctrl+C`.

## Updating

When instructed to update the grader, activate the environment and reinstall it
from GitHub:

```console
conda activate ne111
python -m pip install --upgrade --force-reinstall "uw-ne111-grader @ git+https://github.com/jgostick/UW-NE111-grader.git@main"
```

## Alternative: uvx

If you use [uv](https://docs.astral.sh/uv/getting-started/installation/), no
Conda environment or separate grader installation is required. Run the grader
directly from GitHub:

```console
uvx --python 3.12 --from "git+https://github.com/jgostick/UW-NE111-grader.git@main" ne111-grader A3
```

uv creates and caches an isolated environment automatically. To force it to
check GitHub for an updated version, add `--refresh`:

```console
uvx --refresh --python 3.12 --from "git+https://github.com/jgostick/UW-NE111-grader.git@main" ne111-grader A3
```

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
- `checks.py` contains composable checks for values, exceptions, syntax,
  generated files, NumPy arrays, and returned object attributes.
- `runner.py` is a pure in-process executor with no Streamlit dependency.
- `worker.py` loads and tests a submission in a temporary working directory.
- `isolated.py` manages child processes and enforces timeouts.
- `student_app.py` renders any registered assignment specification.
- `assignments/` contains public test specifications.

The child process protects the Streamlit app from ordinary crashes, import
failures, and infinite loops. It is not a security sandbox: deliberately hostile
submissions require operating-system or container isolation.

Private marker cases live in the separate `UW-NE111-marker` package, which uses
this package's execution engine and result model.
