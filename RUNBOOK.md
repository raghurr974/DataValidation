# Validify Runbook

This runbook documents the implementation, usage, and execution steps for the Validify data validation service.

## Project Overview

Validify is a Python-based data validation framework with both CLI and REST API support. It validates CSV records against configurable rules, including null checks, numeric ranges, date format validation, regex validation, and coordinate validation.

## Key Implementation Components

### 1. CLI Entry Point

- File: `validify/src/validify/main.py`
- Reads a CSV file path from `sys.argv[1]`
- Loads validation rules from `validify/config/rules.yaml`
- Uses `DatasetLoader` to read CSV rows lazily
- Normalizes each row using `normalize_record`
- Runs each record through all configured `BaseValidator` rules
- Builds a `Report` dataclass with total, passed, failed, and results
- Prints a validation summary with pass rate and top failing fields

### 2. Rule Engine and Rules

- File: `validify/src/validify/rules/built_in.py`
- `NullCheckRule`: fails when a field is missing, empty, or whitespace
- `RangeRule`: validates numeric values within configured min/max bounds
- `CoordinateRule`: validates latitude/longitude bounds
- `DateFormatRule`: validates datetime strings against a format
- `RegexRule`: validates fields against a regular expression
- `RuleFactory.from_config()`: loads YAML-defined rule entries and instantiates rule objects

### 3. Rule Registration

- File: `validify/src/validify/rules/registry.py`
- `ValidatorRegistry` uses `__init_subclass__` to auto-register rule classes
- `ValidatorRegistry.get(name)` returns registered rule classes by snake_case type name

### 4. Data Models

- File: `validify/src/validify/core/models.py`
- `ValidationResult`: dataclass for validation outcomes
- `Report`: dataclass that summarizes total, passed, failed, and provides `pass_rate`
- `DataRecord`: dataclass for row metadata (used internally if needed)

### 5. Transforms and CSV Loading

- File: `validify/src/validify/transforms/pipeline.py`
- `normalize_record(record)`: trims whitespace from string values
- `DatasetLoader`: context manager for lazy CSV reading and clean handle closing

### 6. Utility Decorators

- File: `validify/src/validify/utils/decorators.py`
- `@timeit`: measures and prints function runtime
- `@log_call`: logs function call arguments (available if needed)

### 7. API Application

- File: `validify/src/validify/api/app.py`
- FastAPI app with endpoints:
  - `GET /` (root) - API information and endpoint list
  - `GET /health` - Health check
  - `POST /validate` - File upload validation
  - `GET /reports/{run_id}` - Retrieve validation reports
- Uses `RuleFactory` and `run_sequential()` to validate uploaded CSV content
- Stores reports in an in-memory `REPORTS` dictionary

### 8. Execution Engines

- File: `validify/src/validify/engine/runner.py`
- `run_sequential(records, rules)`: baseline sequential validation
- `run_threaded(records, rules, workers=4)`: threaded validation using `ThreadPoolExecutor`
- `run_async(records, rules)`: asynchronous validation with `asyncio` + thread pool
- Built-in timing information is available from `@timeit`

## Directory Structure

```
DataValidation/
├── RUNBOOK.md
├── README.md
├── validify/
│   ├── config/
│   │   └── rules.yaml
│   ├── data/
│   │   └── taxi_trips_sample.csv
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── src/
│   │   └── validify/
│   │       ├── api/
│   │       │   └── app.py
│   │       ├── core/
│   │       │   ├── base.py
│   │       │   ├── exceptions.py
│   │       │   └── models.py
│   │       ├── engine/
│   │       │   └── runner.py
│   │       ├── main.py
│   │       ├── rules/
│   │       │   ├── built_in.py
│   │       │   └── registry.py
│   │       ├── transforms/
│   │       │   └── pipeline.py
│   │       └── utils/
│   │           └── decorators.py
│   └── tests/
│       ├── conftest.py
│       └── test_rules.py
```

## Execution Instructions

### Run from the `validify` directory

This is the recommended working directory for the project.

```powershell
cd "C:\Users\SM335CP\OneDrive - EY\Desktop\Assets\DataValidation\validify"
python src/validify/main.py data/taxi_trips_sample.csv
```

### Run from the repository root

If you are in `DataValidation` root, use the correct path to the CLI script:

```powershell
cd "C:\Users\SM335CP\OneDrive - EY\Desktop\Assets\DataValidation"
python validify/src/validify/main.py validify/data/taxi_trips_sample.csv
```

### Start the API server

From `DataValidation/validify`:

```powershell
cd "C:\Users\SM335CP\OneDrive - EY\Desktop\Assets\DataValidation\validify"
python -m uvicorn validify.api.app:app --reload --host 127.0.0.1 --port 8000
```

## API Endpoints

### Root endpoint

```http
GET /
```

Response:

```json
{
  "message": "Validify Data Validation API",
  "version": "0.1.0",
  "docs": "/docs",
  "endpoints": {
    "health": "GET /health",
    "validate": "POST /validate (upload CSV file)",
    "reports": "GET /reports/{run_id}"
  }
}
```

### Health check

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### Validate file

```http
POST /validate
```

Form data:

- `file`: CSV file upload

Response example:

```json
{
  "run_id": "<uuid>",
  "summary": {
    "total": 200,
    "passed": 110,
    "failed": 90,
    "pass_rate": 55.0
  }
}
```

### Get report

```http
GET /reports/{run_id}
```

Response example:

```json
{
  "total": 200,
  "passed": 110,
  "failed": 90,
  "pass_rate": 55.0,
  "results": [
    {
      "field": "passenger_count",
      "rule": "RangeRule",
      "passed": false,
      "message": "passenger_count: 0.0 is outside [1, 8]"
    }
  ]
}
```

## API Testing

### API Testing with curl

```bash
# Root endpoint (API info)
curl http://127.0.0.1:8000/

# Health check
curl http://127.0.0.1:8000/health

# Upload and validate file
curl -X POST "http://127.0.0.1:8000/validate" \
     -F "file=@data/taxi_trips_sample.csv"

# Get report (replace RUN_ID with actual ID from previous response)
curl http://127.0.0.1:8000/reports/RUN_ID
```

### Interactive API Documentation

When the server is running, visit: http://127.0.0.1:8000/docs

## Testing

### Run unit tests

```powershell
cd "C:\Users\SM335CP\OneDrive - EY\Desktop\Assets\DataValidation\validify"
pytest
```

### Run coverage

```powershell
pytest --cov=src/validify --cov-report=term-missing
```

## Common Issues

### `ConfigError: Rules config file not found: config/rules.yaml`

This happens when the current working directory is not `validify`. Run the CLI from `validify` or supply the correct relative path.

### `405 Method Not Allowed` on `/validate`

The `/validate` endpoint only accepts `POST` requests for file uploads. Use `POST` with form data containing a `file` parameter, not `GET`.

### Correct directory for CLI

From `validify`:

```powershell
python src/validify/main.py data/taxi_trips_sample.csv
```

## Notes

- All rule configuration is defined in `validify/config/rules.yaml`
- The CLI and API both use the same rule loading and validation logic
- The `Report` dataclass provides `pass_rate` and stores all `ValidationResult` entries
- `DatasetLoader` ensures lazy CSV reading and proper file cleanup

---

This file is intended as the authoritative execution guide for the Validify implementation in this repository.
