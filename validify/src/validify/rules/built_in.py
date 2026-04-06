"""
rules/built_in.py — Concrete validation rules and rule factory.

─────────────────────────────────────────────────────────
DAY 1 TASK
─────────────────────────────────────────────────────────
Implement concrete rules as subclasses of BaseValidator.
Each mirrors a function in starter/validate_trips.py:

  NullCheckRule(field: str)
    — Fails when the field is absent, None, or an empty/whitespace string.
    — Mirror of: check_not_null()

  RangeRule(field: str, min: float, max: float)
    — Fails when the field is not a number or is outside [min, max].
    — Mirror of: check_range()

  CoordinateRule(field: str, min: float, max: float)
    — Fails when a geographic coordinate is outside the bounding box.
    — Mirror of: check_coordinate()
    — Hint: the logic is almost identical to RangeRule — what does this
      tell you about inheritance or composition?

Part B (stretch):
  DateFormatRule(field: str, fmt: str = "%Y-%m-%d %H:%M:%S")
    — Fails when the field cannot be parsed as a datetime in the given format.
    — Mirror of: check_date_format()

Each rule must store self.field and any other config params in __init__.
The 'type' name used in config/rules.yaml is the snake_case class name:
  NullCheckRule  → null_check_rule
  RangeRule      → range_rule
  CoordinateRule → coordinate_rule
  DateFormatRule → date_format_rule

─────────────────────────────────────────────────────────
DAY 3 TASK — add RegexRule and RuleFactory
─────────────────────────────────────────────────────────
  RegexRule(field: str, pattern: str)
    — Fails when the field value does not match re.fullmatch(pattern, value).
    — Mirror of: check_allowed_values() but more general.
    — Needed for the payment_type rule in config/rules.yaml.
    — type name: regex_rule

  RuleFactory:
      @staticmethod
      def from_config(path: str) -> list[BaseValidator]:
          # 1. Open and parse the YAML file.
          # 2. For each entry, look up the class: ValidatorRegistry.get(entry["type"])
          # 3. Instantiate it passing the remaining keys as kwargs.
          # 4. Return the list.

─────────────────────────────────────────────────────────
DAY 5 — Git exercise
─────────────────────────────────────────────────────────
On a feature branch, add RegexRule if not done yet, confirm it is
registered and works via a unit test, then merge back to main.
"""

import re  # noqa: F401 — needed by RegexRule
import yaml  # noqa: F401 — needed by RuleFactory
from datetime import datetime

from validify.core.base import BaseValidator  # noqa: F401
from validify.core.exceptions import ConfigError  # noqa: F401
from validify.rules.registry import ValidatorRegistry  # noqa: F401


# ---------------------------------------------------------------------------
# YOUR CODE BELOW
# ---------------------------------------------------------------------------


class NullCheckRule(BaseValidator):
  def __init__(self, field: str) -> None:
    self.field = field
    self._message = ""

  def validate(self, record: dict) -> bool:
    value = record.get(self.field)
    if value is None or str(value).strip() == "":
      self._message = f"{self.field}: value is null or empty"
      return False
    self._message = ""
    return True

  @property
  def message(self) -> str:
    return self._message


class RangeRule(BaseValidator):
  def __init__(self, field: str, min_val: float, max_val: float) -> None:
    self.field = field
    self.min_val = min_val
    self.max_val = max_val
    self._message = ""

  def validate(self, record: dict) -> bool:
    raw = record.get(self.field)
    if raw is None or str(raw).strip() == "":
      self._message = f"{self.field}: value is missing"
      return False

    try:
      value = float(raw)
    except ValueError:
      self._message = f"{self.field}: '{raw}' is not a number"
      return False

    if not (self.min_val <= value <= self.max_val):
      self._message = (
        f"{self.field}: {value} is outside [{self.min_val}, {self.max_val}]"
      )
      return False

    self._message = ""
    return True

  @property
  def message(self) -> str:
    return self._message


class CoordinateRule(BaseValidator):
    """Fail when a geographic coordinate is outside a bounding box.

    Logically identical to RangeRule — a separate class is justified because:
      1. The config/rules.yaml type name 'coordinate_rule' is self-documenting.
      2. Any reader immediately understands what kind of data this checks.
      3. Coordinate-specific behaviour (e.g. validating lon/lat as a pair)
         can be added here without touching the general RangeRule.
    """

    def __init__(self, field: str, min_val: float, max_val: float) -> None:
        self.field = field
        self.min_val = min_val
        self.max_val = max_val
        self._message = ""

    def validate(self, record: dict) -> bool:
        raw = record.get(self.field)
        if raw is None or str(raw).strip() == "":
            self._message = f"{self.field!r} coordinate is missing"
            return False
        try:
            value = float(raw)
        except (ValueError, TypeError):
            self._message = f"{self.field!r} is not a number: {raw!r}"
            return False
        if not (self.min_val <= value <= self.max_val):
            self._message = (
                f"{self.field!r} = {value} out of bounds "
                f"[{self.min_val}, {self.max_val}]"
            )
            return False
        return True

    @property
    def message(self) -> str:
        return self._message


# ---------------------------------------------------------------------------
# DateFormatRule
# ---------------------------------------------------------------------------

class DateFormatRule(BaseValidator):
    """Fails when a field value cannot be parsed as a datetime in the given format.

    Constructor: DateFormatRule(field, fmt="%Y-%m-%d %H:%M:%S")
    """

    def __init__(self, field: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> None:
        self.field = field
        self.fmt = fmt
        self._message = ""

    def validate(self, record: dict) -> bool:
        raw = record.get(self.field)
        if raw is None or str(raw).strip() == "":
            self._message = f"{self.field}: date is missing"
            return False
        try:
            datetime.strptime(str(raw).strip(), self.fmt)
        except ValueError:
            self._message = (
                f"{self.field}: '{raw}' does not match format '{self.fmt}'"
            )
            return False
        self._message = ""
        return True

    @property
    def message(self) -> str:
        return self._message


# ---------------------------------------------------------------------------
# RegexRule
# ---------------------------------------------------------------------------

class RegexRule(BaseValidator):
    """Fails when a field value does not fully match a regex pattern.

    Uses re.fullmatch — the pattern must cover the entire value, not a
    substring.  This gives precise validation (e.g. payment_type whitelist).

    Constructor: RegexRule(field, pattern)
    """

    def __init__(self, field: str, pattern: str) -> None:
        self.field = field
        self.pattern = pattern
        self._message = ""

    def validate(self, record: dict) -> bool:
        raw = record.get(self.field)
        value = str(raw).strip() if raw is not None else ""
        if not re.fullmatch(self.pattern, value):
            self._message = (
                f"{self.field}: '{value}' does not match pattern '{self.pattern}'"
            )
            return False
        self._message = ""
        return True

    @property
    def message(self) -> str:
        return self._message


# ---------------------------------------------------------------------------
# RuleFactory
# ---------------------------------------------------------------------------

class RuleFactory:
    """Builds a list of validator instances from a YAML config file.

    Steps:
      1. Parse the YAML file — it has a top-level "rules" list.
      2. For each entry, look up the class by "type" via ValidatorRegistry.
      3. Strip metadata keys ("name") that aren't constructor arguments.
      4. Remap YAML "min"/"max" → "min_val"/"max_val" to match constructors.
      5. Instantiate with field + remaining kwargs and return the list.
    """

    @staticmethod
    def from_config(path: str) -> list[BaseValidator]:
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except FileNotFoundError as err:
            raise ConfigError(f"Rules config file not found: {path}") from err

        rules: list[BaseValidator] = []
        for entry in data.get("rules", []):
            entry = dict(entry)          # shallow copy — don't mutate YAML data
            entry.pop("name", None)      # "name" is metadata, not a constructor arg
            rule_type = entry.pop("type")
            field = entry.pop("field")

            # YAML uses "min"/"max" but constructors use "min_val"/"max_val"
            # to avoid shadowing Python built-in names.
            if "min" in entry:
                entry["min_val"] = entry.pop("min")
            if "max" in entry:
                entry["max_val"] = entry.pop("max")

            cls = ValidatorRegistry.get(rule_type)
            rules.append(cls(field=field, **entry))

        return rules
