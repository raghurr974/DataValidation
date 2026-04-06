"""
api/app.py — FastAPI application with three routes.

─────────────────────────────────────────────────────────
DAY 4 TASK
─────────────────────────────────────────────────────────
Implement a minimal FastAPI application with these three routes:

  GET  /health
    Returns: {"status": "ok", "version": "0.1.0"}

  POST /validate
    Accepts:  UploadFile (a CSV file)
    Process:
      1. Read the uploaded file bytes and decode to a string.
      2. Parse as CSV using csv.DictReader(io.StringIO(content)).
      3. Load rules from config/rules.yaml.
      4. Run validation using your engine from runner.py.
      5. Build a Report from the results.
      6. Store the Report in the module-level REPORTS dict keyed by a run_id.
      7. Return: {"run_id": "<uuid>", "summary": {"total": N, "passed": N, ...}}

  GET  /reports/{run_id}
    Returns the stored Report as JSON.
    Returns HTTP 404 if run_id is not found.

─────────────────────────────────────────────────────────
TIPS
─────────────────────────────────────────────────────────
  - Use uuid.uuid4() to generate run IDs.
  - Store reports in a module-level dict (not a database).
  - Run with: uvicorn validify.api.app:app --reload
  - The config file is at config/rules.yaml relative to the project root.
    Pass its path as an argument or use an environment variable.
"""

import csv
import io
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile

from validify.core.models import Report
from validify.engine.runner import run_sequential
from validify.rules.built_in import RuleFactory
from validify.transforms.pipeline import normalize_record

# In-memory report store: {run_id: Report}
REPORTS: dict[str, Report] = {}


def create_app() -> FastAPI:
    app = FastAPI(
        title="Validify",
        version="0.1.0",
        description="Enterprise Data Validation & Processing Service",
    )

    # ---------------------------------------------------------------------------
    # YOUR ROUTES BELOW
    # ---------------------------------------------------------------------------

    @app.get("/")
    async def root():
        return {
            "message": "Validify Data Validation API",
            "version": "0.1.0",
            "docs": "/docs",
            "endpoints": {
                "health": "GET /health",
                "validate": "POST /validate (upload CSV file)",
                "reports": "GET /reports/{run_id}"
            }
        }

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": "0.1.0"}

    @app.post("/validate")
    async def validate_file(file: UploadFile):
        # Read the uploaded file
        content = await file.read()
        content_str = content.decode("utf-8")
        
        # Parse CSV
        reader = csv.DictReader(io.StringIO(content_str))
        records = [normalize_record(row) for row in reader]
        
        if not records:
            raise HTTPException(status_code=400, detail="No records found in CSV")
        
        # Load rules
        config_path = Path(__file__).parent.parent / "config" / "rules.yaml"
        rules = RuleFactory.from_config(str(config_path))
        
        # Run validation
        results = run_sequential(records, rules)
        
        # Count passed/failed
        total = len(records)
        passed = sum(1 for result in results if result.passed)
        failed = total - passed
        
        # Create report
        report = Report(total=total, passed=passed, failed=failed, results=results)
        
        # Generate run_id and store report
        run_id = str(uuid.uuid4())
        REPORTS[run_id] = report
        
        return {
            "run_id": run_id,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": report.pass_rate
            }
        }

    @app.get("/reports/{run_id}")
    async def get_report(run_id: str):
        if run_id not in REPORTS:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report = REPORTS[run_id]
        return {
            "total": report.total,
            "passed": report.passed,
            "failed": report.failed,
            "pass_rate": report.pass_rate,
            "results": [
                {
                    "field": result.field,
                    "rule": result.rule,
                    "passed": result.passed,
                    "message": result.message
                }
                for result in report.results
            ]
        }

    return app


app = create_app()
