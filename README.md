# UW NE 111 Checker

Reusable grading engine and student-facing Streamlit app for UW NE 111
assignments.

## Student installation

Git is not required. Choose the instructions for your computer:

<details open>
<summary><strong>Windows — Anaconda Prompt</strong></summary>

Open **Anaconda Prompt** from the Start menu, then run:

```console
python -m pip install "https://github.com/jgostick/UW-NE111-checker/archive/refs/heads/main.zip"
```

</details>

<details>
<summary><strong>macOS — Terminal</strong></summary>

Open **Terminal**, then run:

```console
python3 -m pip install "https://github.com/jgostick/UW-NE111-checker/archive/refs/heads/main.zip"
```

</details>

## Using the checker

For each work session, launch the required assignment (`A1` through `A9`).
Use these commands rather than a bare `ne111-checker` command: they always use
the same Python installation that installed the checker.

<details open>
<summary><strong>Windows</strong></summary>

```console
python -m ne111_checker A3
```

</details>

<details>
<summary><strong>macOS</strong></summary>

```console
python3 -m ne111_checker A3
```

</details>

The checker opens in a browser. It reads the expected submission filename from
the folder where you launched it: `A1.ipynb` and `A2.ipynb` for the notebook
assignments, and `A<N>.py` for the function-based assignments. Select a
question tab and press its **Run** button.

Notebook assignments use tagged code cells. Put `# A1Q3` or `# A2Q3` (using the
applicable assignment and question ID) on the first nonblank line of the answer cell, then
assign the result to `answer`. The handout specifies the input-variable names;
the checker injects a fresh set of inputs and reruns the tagged cell for every
case. Cells tagged `# setup` run before each answer cell. Notebook outputs and
metadata are not executed.

If the file is named `A3.py` and the command is run from the same directory, it
is selected automatically. A path can also be supplied explicitly; use
`python3` rather than `python` on macOS:

```console
python -m ne111_checker A3 --submission path/to/A3.py
```

To stop the Streamlit server, return to the terminal where you launched it and
press `Ctrl+C`. On Windows, `Ctrl+Break` (or `Ctrl+Fn+Pause` on some laptops) is
an alternative if `Ctrl+C` is intercepted by the terminal.

## Updating

When instructed to update the checker, run the appropriate command:

<details open>
<summary><strong>Windows</strong></summary>

```console
python -m pip install --upgrade --force-reinstall --no-cache-dir "https://github.com/jgostick/UW-NE111-checker/archive/refs/heads/main.zip"
```

</details>

<details>
<summary><strong>macOS</strong></summary>

```console
python3 -m pip install --upgrade --force-reinstall --no-cache-dir "https://github.com/jgostick/UW-NE111-checker/archive/refs/heads/main.zip"
```

</details>

## Alternative: uvx

If you use [uv](https://docs.astral.sh/uv/getting-started/installation/), no
Conda environment or separate checker installation is required. Run the checker
directly from GitHub:

```console
uvx --python 3.12 --from "git+https://github.com/jgostick/UW-NE111-checker.git@main" ne111-checker A3
```

uv creates and caches an isolated environment automatically. To force it to
check GitHub for an updated version, add `--refresh`:

```console
uvx --refresh --python 3.12 --from "git+https://github.com/jgostick/UW-NE111-checker.git@main" ne111-checker A3
```

## Development

Create a local environment from the repository:

```console
conda env create --file environment.yml
conda activate ne111
pytest
python -m ne111_checker A1 --submission path/to/A1.py
```

Alternatively, with uv:

```console
uv run --extra dev pytest
uv run ne111-checker A1 --submission path/to/A1.py
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
