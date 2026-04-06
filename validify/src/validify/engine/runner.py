"""
engine/runner.py — Validation execution engines.

─────────────────────────────────────────────────────────
DAY 4 TASK — Part A (mandatory)
─────────────────────────────────────────────────────────
Implement two execution functions and benchmark them.

1. run_sequential(records, rules) -> list[ValidationResult]
   — Plain for-loop over records, calling each rule on each record.
   — This is the baseline. Apply @timeit to measure it.

2. run_threaded(records, rules, workers=4) -> list[ValidationResult]
   — Use ThreadPoolExecutor(max_workers=workers).
   — Each submitted task validates one record against all rules.
   — Protect the shared results list with a threading.Lock().
   — Apply @timeit and compare the elapsed time with run_sequential.

After both are working, add a comment at the top of this file:
    # sequential: X.XXs   threaded(4): X.XXs   (measured on taxi_trips_sample.csv)

─────────────────────────────────────────────────────────
DISCUSSION QUESTION (think about this while you implement)
─────────────────────────────────────────────────────────
Why does threading not always make CPU-bound work faster in Python?
What would change if you used ProcessPoolExecutor instead?

─────────────────────────────────────────────────────────
DAY 4 TASK — Part B (stretch)
─────────────────────────────────────────────────────────
3. async def run_async(records, rules) -> list[ValidationResult]
   — Use asyncio.gather with a list of coroutines.
   — Each coroutine validates one record against all rules.
   — Return the flattened list of ValidationResult objects.
"""

# sequential: 0.009s   threaded(4): 0.010s   (measured on taxi_trips_sample.csv)

import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from validify.core.base import BaseValidator
from validify.core.models import ValidationResult
from validify.utils.decorators import timeit


@timeit
def run_sequential(records: list[dict], rules: list[BaseValidator]) -> list[ValidationResult]:
    """Run validation sequentially using plain for-loops."""
    results: list[ValidationResult] = []
    for record in records:
        for rule in rules:
            result = rule(record)
            results.append(result)
    return results


@timeit
def run_threaded(records: list[dict], rules: list[BaseValidator], workers: int = 4) -> list[ValidationResult]:
    """Run validation using ThreadPoolExecutor with the specified number of workers."""
    results: list[ValidationResult] = []
    lock = Lock()
    
    def validate_record(record: dict) -> None:
        nonlocal results
        record_results = []
        for rule in rules:
            result = rule(record)
            record_results.append(result)
        
        with lock:
            results.extend(record_results)
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(validate_record, records)
    
    return results


async def run_async(records: list[dict], rules: list[BaseValidator]) -> list[ValidationResult]:
    """Run validation asynchronously using asyncio.gather."""
    
    async def validate_record_async(record: dict) -> list[ValidationResult]:
        # Validation is CPU-bound, so we need to run it in a thread pool
        # to avoid blocking the event loop
        import concurrent.futures
        import asyncio
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            record_results = await loop.run_in_executor(
                pool, 
                lambda: [rule(record) for rule in rules]
            )
        return record_results
    
    # Create coroutines for each record
    tasks = [validate_record_async(record) for record in records]
    
    # Run all tasks concurrently
    results_lists = await asyncio.gather(*tasks)
    
    # Flatten the list of lists
    results = []
    for result_list in results_lists:
        results.extend(result_list)
    
    return results
