# UW NE 111 Checker

Reusable grading engine and student-facing Streamlit app for UW NE 111
assignments.

## Student installation

Do this once in Anaconda Prompt on Windows or a terminal on macOS:

```console
python -m pip install "uw-ne111-checker @ git+https://github.com/jgostick/UW-NE111-checker.git@main"
```

### Optional: use an isolated Conda environment

The checker has ordinary Python dependencies and can be installed into the
Anaconda base environment. If you prefer an isolated environment, create and
activate it before running the installation command:

```console
conda create -n ne111 python=3.12 pip git -y
conda activate ne111
python -m pip install "uw-ne111-checker @ git+https://github.com/jgostick/UW-NE111-checker.git@main"
```

## Using the checker

For each work session, launch the required assignment (`A1` through `A9`).
Use this form rather than a bare `ne111-checker` command: it always uses the
same Python installation that installed the checker.

```console
python -m ne111_checker A3
```

If you chose the optional Conda environment, run `conda activate ne111` first.

The checker opens in a browser. It reads the expected submission filename from
the folder where you launched it: `A1.ipynb` for A1 and `A<N>.py` for the
function-based assignments. Select a question tab and press its **Run** button.

Notebook assignments use tagged code cells. Put `# A1Q3` (using the applicable
assignment and question ID) on the first nonblank line of the answer cell, then
assign the result to `answer`. The handout specifies the input-variable names;
the checker injects a fresh set of inputs and reruns the tagged cell for every
case. Cells tagged `# setup` run before each answer cell. Notebook outputs and
metadata are not executed.

If the file is named `A3.py` and the command is run from the same directory, it
is selected automatically. A path can also be supplied explicitly:

```console
python -m ne111_checker A3 --submission path/to/A3.py
```

Stop the Streamlit server by returning to Anaconda Prompt and pressing `Ctrl+C`.
On Windows, `Ctrl+Break` (or `Ctrl+Fn+Pause` on some laptops) is an alternative
if `Ctrl+C` is intercepted by the terminal.

## Updating

When instructed to update the checker, reinstall it from GitHub:

```console
python -m pip install --upgrade --force-reinstall "uw-ne111-checker @ git+https://github.com/jgostick/UW-NE111-checker.git@main"
```

If you chose the optional Conda environment, activate it before running this
command.

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
