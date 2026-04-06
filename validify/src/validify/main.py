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

import sys
from collections import defaultdict
from pathlib import Path

from validify.core.models import ValidationResult, Report
from validify.rules.built_in import RuleFactory
from validify.transforms.pipeline import DatasetLoader, normalize_record
from validify.utils.decorators import timeit


def aggregate_by_field(results: list[ValidationResult]) -> dict[str, int]:
  counts: dict[str, int] = defaultdict(int)
  for result in results:
    if not result.passed:
      counts[result.field] += 1
  return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def print_report(report: Report, failed_rows: list[dict[str, object]]) -> None:
  line = "=" * 60
  print(f"\n{line}")
  print("VALIDATION REPORT")
  print(line)
  print(f"  Total records : {report.total}")
  print(f"  Passed        : {report.passed}")
  print(f"  Failed        : {report.failed}")
  print(f"  Pass rate     : {report.pass_rate}%")

  if failed_rows:
    field_counts = aggregate_by_field(report.results)
    print("\n  Top failing fields:")
    for field, count in list(field_counts.items())[:5]:
      pct = count / report.total * 100
      print(f"    {field:<28} {count:>4} failures  ({pct:.1f}%)")

    print("\nFailed rows (first 10):")
    for item in failed_rows[:10]:
      messages = "; ".join(item["messages"])  # type: ignore[arg-type]
      print(f"  Row {item['row']:>4} | {messages}")
    if len(failed_rows) > 10:
      print(f"  ... and {len(failed_rows) - 10} more.")

  print(line)


@timeit
def run_validation(csv_path: Path) -> tuple[Report, list]:
  rules = RuleFactory.from_config("config/rules.yaml")

  total = 0
  passed = 0
  failed = 0
  all_results: list[ValidationResult] = []
  failed_rows: list[dict[str, object]] = []

  with DatasetLoader(str(csv_path)) as records:
    for row_num, record in enumerate(records, start=2):
      total += 1
      normalized_record = normalize_record(record)
      row_messages: list[str] = []
      for rule in rules:
        result = rule(normalized_record)
        all_results.append(result)
        if not result.passed:
          row_messages.append(result.message)

      if row_messages:
        failed += 1
        failed_rows.append({"row": row_num, "messages": row_messages})
      else:
        passed += 1

  report = Report(total=total, passed=passed, failed=failed, results=all_results)
  return report, failed_rows


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python src/validify/main.py <path/to/trips.csv>")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: file not found — {csv_path}")
        sys.exit(1)

    report, failed_rows = run_validation(csv_path)
    if report.total == 0:
      print("No records found in the file.")
      sys.exit(1)

    print_report(report, failed_rows)


if __name__ == "__main__":
    main()
