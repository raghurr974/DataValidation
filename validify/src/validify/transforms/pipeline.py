"""
transforms/pipeline.py — Functional transformation pipeline.

─────────────────────────────────────────────────────────
DAY 3 TASK — Part A (mandatory)
─────────────────────────────────────────────────────────
1. Implement pipe(*fns) using functools.reduce:

       pipe(f, g, h)(x)  ==  h(g(f(x)))

   Each function takes one value and returns one value.
   Use functools.reduce to chain them left to right.

   Example:
       strip  = lambda d: {k: v.strip() for k, v in d.items()}
       result = pipe(strip, normalize_record)(raw_record)

2. Implement normalize_record(record: dict) -> dict:
   - Strip leading/trailing whitespace from all string values.
   - That is the minimum. Keep it simple.

─────────────────────────────────────────────────────────
DAY 3 TASK — Part B (stretch)
─────────────────────────────────────────────────────────
3. Implement DatasetLoader as a context manager:

       class DatasetLoader:
           def __init__(self, path: str) -> None: ...
           def __enter__(self) -> Iterator[dict]: ...
           def __exit__(self, *args) -> None: ...

   - Opens the CSV file in __enter__.
   - Yields a generator of dict rows (one per CSV row).
   - Does NOT load the full file into memory (use csv.DictReader lazily).
   - Closes the file handle in __exit__.
   - Raises DataLoadError (from core.exceptions) if the file is not found.

   Usage in main.py (after implementation):
       with DatasetLoader("data/taxi_trips_sample.csv") as records:
           for record in records:
               ...
"""

import csv  # noqa: F401
from functools import reduce  # noqa: F401
from typing import Callable, Iterator, TypeVar  # noqa: F401

from validify.core.exceptions import DataLoadError  # noqa: F401

T = TypeVar("T")


# ---------------------------------------------------------------------------
# YOUR CODE BELOW
# ---------------------------------------------------------------------------


def pipe(*fns: Callable) -> Callable:
    """Chain functions left to right so pipe(f, g, h)(x) == h(g(f(x))).

    Uses functools.reduce to fold the function list over an initial value.
    reduce starts with the input x as the accumulator, then applies each
    function in sequence:
        Step 1: acc = f(x)
        Step 2: acc = g(acc)
        Step 3: acc = h(acc)
    """
    return lambda x: reduce(lambda acc, fn: fn(acc), fns, x)


def normalize_record(record: dict) -> dict:
    """Strip leading/trailing whitespace from every string value in a record.

    Non-string values (numbers, None, etc.) are passed through unchanged.
    This is typically the first transform applied before rules run.
    """
    return {k: v.strip() if isinstance(v, str) else v for k, v in record.items()}


class DatasetLoader:
    """Context manager for lazy, memory-efficient CSV reading.

    Opens the file in __enter__ and returns a csv.DictReader generator.
    The file is never fully loaded into memory — rows are yielded one at a
    time, which is important for large datasets.

    Raises DataLoadError if the file path does not exist.

    Usage:
        with DatasetLoader("data/taxi_trips_sample.csv") as records:
            for record in records:
                ...
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._file = None

    def __enter__(self) -> Iterator[dict]:
        try:
            self._file = open(self._path, newline="", encoding="utf-8")
        except FileNotFoundError as err:
            raise DataLoadError(path=self._path, reason="file not found") from err
        return csv.DictReader(self._file)

    def __exit__(self, *args) -> None:
        if self._file is not None:
            self._file.close()
