"""
core/base.py — Abstract base classes for the Validify plugin system.

─────────────────────────────────────────────────────────
DAY 1 TASK
─────────────────────────────────────────────────────────
Implement BaseValidator(ABC):

  Abstract method:
      validate(self, record: dict) -> bool
      — Returns True if the record passes, False if it fails.

  Abstract property:
      message(self) -> str
      — Returns the human-readable error description when validate() is False.
      — Return "" (empty string) when there is no failure.

  Concrete method (provide this yourself):
      __call__(self, record: dict) -> ValidationResult
      — Calls self.validate(record)
      — Returns ValidationResult(
             field=self.field,   # the field name this rule checks
             rule=type(self).__name__,
             passed=<result>,
             message=self.message if not passed else "",
         )

Note: every concrete rule (NullCheckRule, RangeRule …) stores the target
field name in self.field. You will set this in each rule's __init__.

─────────────────────────────────────────────────────────
DAY 2 TASK
─────────────────────────────────────────────────────────
After implementing ValidatorRegistry in rules/registry.py,
add it as a second base class here:

    class BaseValidator(ValidatorRegistry, ABC):
        ...

This makes every subclass of BaseValidator automatically register itself.

─────────────────────────────────────────────────────────
"""

from abc import ABC, abstractmethod

from validify.core.models import ValidationResult  # noqa: F401
from validify.rules.registry import ValidatorRegistry


# ---------------------------------------------------------------------------
# YOUR CODE BELOW
# ---------------------------------------------------------------------------
class BaseValidator(ValidatorRegistry, ABC):
    @abstractmethod
    def validate(self, record: dict) -> bool:
        """Returns True if the record passes, False if it fails."""

    @property
    @abstractmethod
    def message(self) -> str:
        """Error description for the most recent failed validation."""

    def __call__(self, record: dict) -> ValidationResult:
        passed = self.validate(record)
        return ValidationResult(
            field=self.field,
            rule=type(self).__name__,
            passed=passed,
            message=self.message if not passed else "",
        )