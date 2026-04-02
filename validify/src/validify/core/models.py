"""
core/models.py — Domain models for Validify.

─────────────────────────────────────────────────────────
DAY 1 TASK
─────────────────────────────────────────────────────────
Implement ValidationResult as a plain class (not a dataclass yet):

    class ValidationResult:
        def __init__(self, field, rule, passed, message):
            ...

Fields:
  field   (str)  — the CSV column name that was checked
  rule    (str)  — the rule class name (e.g. "NullCheckRule")
  passed  (bool) — True if the check succeeded
  message (str)  — human-readable description of the failure ("" if passed)

─────────────────────────────────────────────────────────
DAY 2 TASK
─────────────────────────────────────────────────────────
1. Convert ValidationResult to @dataclass.
   Add __repr__ (automatic with dataclass) and confirm __eq__ works.

2. Add DataRecord dataclass:
      row_number : int
      fields     : dict[str, str]

3. Add Report dataclass:
      total   : int
      passed  : int
      failed  : int
      results : list[ValidationResult]   ← use field(default_factory=list)

   Add a @property:
      pass_rate -> float   (0.0 to 100.0, rounded to 1 decimal)

Hint: import dataclass and field from the dataclasses module.
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# YOUR CODE BELOW
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    field: str
    rule: str
    passed: bool
    message: str


@dataclass
class DataRecord:
    row_number: int
    fields: dict[str, str]


@dataclass
class Report:
    total: int
    passed: int
    failed: int
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.passed / self.total) * 100, 1)