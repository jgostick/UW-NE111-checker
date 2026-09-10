from __future__ import annotations

import textwrap

import pytest

from ne111_grader.isolated import run_question_isolated
from ne111_grader.registry import get_assignment

SOURCES = {
    "A3": """
def A3Q1(value): return sum(character.isalpha() for character in value)
def A3Q2(value): return len(value.replace(' ', ''))
def A3Q3(password):
    special = '!@#$%^&'
    return (any(c.isupper() for c in password)
            and any(c.islower() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in special for c in password))
def A3Q4(email, domain): return email.endswith(domain)
def A3Q5(filenames, extension):
    extension = extension.removeprefix('.')
    return [name for name in filenames if name.endswith('.' + extension)]
def A3Q6(a, b): return a < b
def A3Q7(values): return ''.join(values)
def A3Q8(value):
    return dict(item.split(':') for item in value.split(';'))
def A3Q9(message, number, mode):
    import random
    import string
    if mode == 'encrypt':
        return ''.join(
            character + ''.join(random.choices(string.ascii_letters, k=number))
            for character in message
        )
    if mode == 'decrypt':
        return message[::number + 1]
    raise ValueError('mode must be encrypt or decrypt')
""",
    "A4": """
def A4Q1(filename):
    with open(filename) as file: return len(file.read().splitlines())
def A4Q2(filename):
    with open(filename) as file: return len(file.read().split())
def A4Q3(filename, value, repetitions):
    with open(filename, 'w') as file:
        for _ in range(repetitions): file.write(value.strip('\\n') + '\\n')
def A4Q4(filename, data):
    import pandas as pd
    if not filename.endswith('.csv'): filename += '.csv'
    pd.DataFrame(data).to_csv(filename, index=False)
def A4Q5(filename):
    import pandas as pd
    if not filename.endswith('.csv'): filename += '.csv'
    return pd.read_csv(filename).to_dict(orient='list')
def A4Q6(filename, value):
    with open(filename, 'a') as file: file.write('\\n' + value)
""",
    "A5": """
def A5Q1(c, start=None, stop=None, step=None):
    return c[start:stop:step]
def A5Q2(first, second):
    first, second = set(first), set(second)
    return first & second, first ^ second
def A5Q3(a, b=1, c=5):
    ans1 = (-b + (b**2 - 4 * a * c) ** 0.5) / (2 * a)  # One root
    ans2 = (-b - (b**2 - 4 * a * c) ** 0.5) / (2 * a)  # The other root
    return (ans1, ans2)
def A5Q4(a, b):
    try: return a * b
    except TypeError: return None
def A5Q5(a, b=1, c=1, d=1): return a * b * c * d
def A5Q6(a, b, c=0):
    \"\"\"Compute a Euclidean length.

    Parameters
    ----------
    a : float
        First component.
    b : float
        Second component.
    c : float
        Third component.

    Returns
    -------
    float
        The Euclidean length.
    \"\"\"
    return (a**2 + b**2 + c**2)**0.5
""",
    "A6": """
import numpy as np
def A6Q1(array): return np.asarray(array).astype(int)
def A6Q2(radius):
    radius = np.asarray(radius)
    return np.column_stack((4 / 3 * np.pi * radius**3, 4 * np.pi * radius**2))
def A6Q3(array, split):
    array = np.asarray(array); row, column = split
    return [[array[:row, :column], array[:row, column:]],
            [array[row:, :column], array[row:, column:]]]
def A6Q4(array, threshold):
    array = np.asarray(array)
    return ((array < threshold).sum(), (array == threshold).sum(),
            (array > threshold).sum())
def A6Q5(array):
    array = np.asarray(array)
    return (array - array.min()) / (array.max() - array.min())
def A6Q6(array):
    array = np.asarray(array)
    return np.vstack((array.max(axis=0), array.min(axis=0)))
def A6Q7(first, second):
    answers = []
    for function in (np.vstack, np.hstack):
        try: answers.append(function((first, second)))
        except ValueError: pass
    return answers[0] if len(answers) == 1 else None
def A6Q8(array):
    array = np.asarray(array)
    return array[array % 2 == 0].sum()
""",
    "A7": """
import numpy as np
def A7Q1(first, second):
    try: np.broadcast_arrays(first, second); return True
    except ValueError: return False
def A7Q2(first, second, symbol):
    operations = {'+': np.add, '-': np.subtract, '*': np.multiply,
                  '/': np.divide, '//': np.floor_divide,
                  '%': np.mod, '**': np.power}
    return operations[symbol](first, second)
def A7Q3(points):
    points = np.asarray(points)
    return ((points[:, 0].min(), points[:, 1].min()),
            (points[:, 0].max(), points[:, 1].max()))
def A7Q4(vector):
    vector = np.asarray(vector)
    return vector / np.linalg.norm(vector)
def A7Q5(matrix, vector): return np.matmul(matrix, vector).flatten()
def A7Q6(matrix):
    matrix = np.asarray(matrix)
    mask = np.eye(matrix.shape[0], dtype=bool)
    return matrix[mask].sum()
def A7Q7(matrix):
    matrix = np.asarray(matrix)
    return np.allclose(matrix, np.triu(matrix)) or np.allclose(matrix, np.tril(matrix))
""",
    "A8": """
import numpy as np
import matplotlib.pyplot as plt
def A8Q1(x, y):
    figure, axes = plt.subplots(); axes.scatter(x, y); return figure, axes
def A8Q2(*arrays):
    figure, axes = plt.subplots(1, len(arrays))
    for axis, array in zip(axes, arrays): axis.hist(array)
    return figure, axes
def A8Q3(image):
    figure, axes = plt.subplots(); axes.imshow(image); return figure, axes
def A8Q4(figure, color): figure.set_facecolor(color); return figure
def A8Q5(x, y):
    x, y = np.asarray(x), np.asarray(y)
    valid = (x >= 0) & (x <= 1) & (y >= 0) & (y <= 1)
    figure, axes = plt.subplots(); axes.scatter(x[valid], y[valid]); return figure, axes
""",
}

EXPECTED_CASES = {"A3": 22, "A4": 6, "A5": 14, "A6": 8, "A7": 15, "A8": 9}


@pytest.mark.parametrize("assignment_id", tuple(SOURCES))
def test_reference_submission_passes(assignment_id, tmp_path) -> None:
    submission = tmp_path / f"{assignment_id}.py"
    submission.write_text(textwrap.dedent(SOURCES[assignment_id]), encoding="utf-8")
    assignment = get_assignment(assignment_id)

    results = tuple(
        run_question_isolated(assignment_id, question.id, submission)
        for question in assignment.questions
    )

    assert all(result.passed for result in results)
    assert sum(len(result.cases) for result in results) == EXPECTED_CASES[assignment_id]
