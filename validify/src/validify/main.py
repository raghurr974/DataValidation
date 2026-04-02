"""
src/validify/main.py — CLI entry point for the validation pipeline.

─────────────────────────────────────────────────────────
DAY 1 TASK (create this file)
─────────────────────────────────────────────────────────
Create a runner that produces the same output as starter/validate_trips.py
but uses the new class hierarchy:

  1. Accept a CSV path from sys.argv[1].
  2. Open the CSV with open() + csv.DictReader (plain, no context manager yet).
  3. Instantiate rules manually:
       rules = [NullCheckRule("vendor_id"), RangeRule("passenger_count", 1, 8), ...]
  4. For each record, call each rule: result = rule(record)  # __call__
  5. Collect ValidationResult objects.
  6. Print a summary (same format as the starter script).

─────────────────────────────────────────────────────────
DAY 2 TASK (update this file)
─────────────────────────────────────────────────────────
  - Apply @timeit to the main validation function.
  - Build a Report dataclass from the results and print pass_rate from it.

─────────────────────────────────────────────────────────
DAY 3 TASK (update this file)
─────────────────────────────────────────────────────────
  - Replace the hardcoded rules list with:
      rules = RuleFactory.from_config("config/rules.yaml")
  - Wrap the CSV open() in DatasetLoader context manager (stretch).
  - Run records through normalize_record before validation.

─────────────────────────────────────────────────────────
Run with:
    python src/validify/main.py data/taxi_trips_sample.csv
─────────────────────────────────────────────────────────
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

from validify.core.models import ValidationResult
from validify.rules.built_in import NullCheckRule, RangeRule


def aggregate_by_field(results: list[ValidationResult]) -> dict[str, int]:
  counts: dict[str, int] = defaultdict(int)
  for result in results:
    if not result.passed:
      counts[result.field] += 1
  return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def print_report(
  total: int,
  passed: int,
  failed: int,
  failed_rows: list[dict[str, object]],
  results: list[ValidationResult],
) -> None:
  line = "=" * 60
  print(f"\n{line}")
  print("VALIDATION REPORT")
  print(line)
  print(f"  Total records : {total}")
  print(f"  Passed        : {passed}")
  print(f"  Failed        : {failed}")
  print(f"  Pass rate     : {passed / total * 100:.1f}%")

  if failed_rows:
    field_counts = aggregate_by_field(results)
    print("\n  Top failing fields:")
    for field, count in list(field_counts.items())[:5]:
      pct = count / total * 100
      print(f"    {field:<28} {count:>4} failures  ({pct:.1f}%)")

    print("\nFailed rows (first 10):")
    for item in failed_rows[:10]:
      row = item["row"]
      messages = "; ".join(item["messages"])  # type: ignore[arg-type]
      print(f"  Row {row:>4} | {messages}")
    if len(failed_rows) > 10:
      print(f"  ... and {len(failed_rows) - 10} more.")

  print(line)


def run_validation(csv_path: Path) -> tuple[int, int, int, list[dict[str, object]], list[ValidationResult]]:
  rules = [
    NullCheckRule("vendor_id"),
    RangeRule("passenger_count", 1, 8),
    RangeRule("trip_distance", 0.1, 200.0),
    RangeRule("fare_amount", 0.01, 500.0),
  ]

  total = 0
  passed = 0
  failed = 0
  failed_rows: list[dict[str, object]] = []
  all_results: list[ValidationResult] = []

  fh = open(csv_path, newline="", encoding="utf-8")
  try:
    reader = csv.DictReader(fh)
    for row_num, record in enumerate(reader, start=2):
      total += 1
      row_messages: list[str] = []
      for rule in rules:
        result = rule(record)
        all_results.append(result)
        if not result.passed:
          row_messages.append(result.message)

      if row_messages:
        failed += 1
        failed_rows.append({"row": row_num, "messages": row_messages})
      else:
        passed += 1
  finally:
    fh.close()

  return total, passed, failed, failed_rows, all_results


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python src/validify/main.py <path/to/trips.csv>")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: file not found — {csv_path}")
        sys.exit(1)

    total, passed, failed, failed_rows, results = run_validation(csv_path)
    if total == 0:
      print("No records found in the file.")
      sys.exit(1)

    print_report(total, passed, failed, failed_rows, results)


if __name__ == "__main__":
    main()
