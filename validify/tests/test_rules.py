"""
tests/test_rules.py — Unit tests for built-in validation rules.

─────────────────────────────────────────────────────────
DAY 5 TASK
─────────────────────────────────────────────────────────
Write exactly 5 tests (the ones named below). Then run:

    pytest --cov=src/validify --cov-fail-under=70

All 5 tests must pass. The coverage threshold must be met.

Use the fixtures from conftest.py: valid_record, null_record, out_of_range_record.
"""

import pytest

from validify.rules.built_in import DateFormatRule, NullCheckRule, RangeRule, RegexRule, RuleFactory
from validify.rules.registry import ValidatorRegistry


# ---------------------------------------------------------------------------
# Test 1
# ---------------------------------------------------------------------------
def test_null_check_passes_when_field_present(valid_record):
    """NullCheckRule.validate() should return True for a non-empty vendor_id."""
    rule = NullCheckRule(field="vendor_id")
    assert rule.validate(valid_record) is True


# ---------------------------------------------------------------------------
# Test 2
# ---------------------------------------------------------------------------
def test_null_check_fails_when_field_empty(null_record):
    """NullCheckRule.validate() should return False when passenger_count is ''."""
    rule = NullCheckRule(field="passenger_count")
    assert rule.validate(null_record) is False


# ---------------------------------------------------------------------------
# Test 3
# ---------------------------------------------------------------------------
def test_range_rule_passes_within_bounds(valid_record):
    """RangeRule should pass when passenger_count == 1 and bounds are [1, 8]."""
    rule = RangeRule(field="passenger_count", min_val=1, max_val=8)
    assert rule.validate(valid_record) is True


# ---------------------------------------------------------------------------
# Test 4
# ---------------------------------------------------------------------------
def test_range_rule_fails_above_max(out_of_range_record):
    """RangeRule should fail when passenger_count == 12 and max is 8."""
    rule = RangeRule(field="passenger_count", min_val=1, max_val=8)
    assert rule.validate(out_of_range_record) is False


# ---------------------------------------------------------------------------
# Test 5
# ---------------------------------------------------------------------------
def test_registry_has_null_check_rule():
    """
    Importing NullCheckRule should auto-register it in ValidatorRegistry.
    ValidatorRegistry.get("null_check_rule") should return the NullCheckRule class.
    """
    assert ValidatorRegistry.get("null_check_rule") is NullCheckRule


# ---------------------------------------------------------------------------
# Stretch tests (optional — write after the 5 mandatory ones)
# ---------------------------------------------------------------------------
def test_date_format_rule_passes_valid_date(valid_record):
    """DateFormatRule should pass when pickup_datetime matches the expected format."""
    rule = DateFormatRule(field="pickup_datetime", fmt="%Y-%m-%d %H:%M:%S")
    assert rule.validate(valid_record) is True


def test_date_format_rule_fails_invalid_date():
    """DateFormatRule should fail when pickup_datetime is not a valid date."""
    invalid_record = {
        "pickup_datetime": "not-a-date",
        "passenger_count": "1",
    }
    rule = DateFormatRule(field="pickup_datetime", fmt="%Y-%m-%d %H:%M:%S")
    assert rule.validate(invalid_record) is False


def test_regex_rule_passes_matching_value(valid_record):
    """RegexRule should pass when payment_type matches the pattern."""
    rule = RegexRule(field="payment_type", pattern=r"^(Credit|Cash|No Charge|Dispute)$")
    assert rule.validate(valid_record) is True


def test_regex_rule_fails_non_matching_value(null_record):
    """RegexRule should fail when payment_type doesn't match the pattern."""
    # Modify null_record to have an invalid payment_type
    test_record = null_record.copy()
    test_record["payment_type"] = "invalid"
    rule = RegexRule(field="payment_type", pattern=r"^(Credit|Cash|No Charge|Dispute)$")
    assert rule.validate(test_record) is False


def test_rule_factory_loads_from_yaml():
    """RuleFactory.from_config should load and instantiate rules from YAML."""
    rules = RuleFactory.from_config("config/rules.yaml")
    assert len(rules) > 0
    # Check that we have the expected types of rules
    rule_types = {type(rule).__name__ for rule in rules}
    assert "NullCheckRule" in rule_types
    assert "RangeRule" in rule_types
    assert "DateFormatRule" in rule_types
    assert "RegexRule" in rule_types
