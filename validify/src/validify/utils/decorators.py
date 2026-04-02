"""
utils/decorators.py — Reusable function decorators.

─────────────────────────────────────────────────────────
DAY 2 TASK — Part A (mandatory)
─────────────────────────────────────────────────────────
Implement @timeit:
  - Measures wall-clock time from before to after the function call.
  - Prints: [timeit] <function_name> took 0.042s
  - Must preserve the original function's __name__ and __doc__ (use functools.wraps).
  - Works on synchronous functions first.

Usage:
    @timeit
    def run_validation(records, rules):
        ...

─────────────────────────────────────────────────────────
DAY 2 TASK — Part B (stretch)
─────────────────────────────────────────────────────────
Implement @log_call:
  - Prints: [log_call] calling <function_name>(<arg1>, kwarg=<value>)
  - Must use functools.wraps.
  - Useful for tracing which rules run on which records during debugging.

Usage:
    @log_call
    def validate(self, record):
        ...

─────────────────────────────────────────────────────────
HINTS
─────────────────────────────────────────────────────────
  - Use functools.wraps to preserve the original function's metadata.
  - Use time.perf_counter() (not time.time()) for accurate elapsed time.
  - A decorator is just a function that takes a function and returns a function.
"""

import functools
import time
from typing import Any, Callable, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# YOUR CODE BELOW
# ---------------------------------------------------------------------------


def timeit(func: F) -> F:
  @functools.wraps(func)
  def wrapper(*args: Any, **kwargs: Any) -> Any:
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    print(f"[timeit] {func.__name__} took {elapsed:.3f}s")
    return result

  return cast(F, wrapper)


def log_call(func: F) -> F:
  @functools.wraps(func)
  def wrapper(*args: Any, **kwargs: Any) -> Any:
    parts = [repr(arg) for arg in args]
    parts.extend(f"{key}={value!r}" for key, value in kwargs.items())
    print(f"[log_call] calling {func.__name__}({', '.join(parts)})")
    return func(*args, **kwargs)

  return cast(F, wrapper)
