# Employee Data Analysis

A secure, local-first employee CSV analysis application built with Python, FastAPI, and Pandas.

## Project purpose

The application accepts an employee CSV upload, validates the file and required fields, computes aggregate salary metrics, filters records by a user-provided threshold, and exports a sanitized CSV file in a managed output directory.

## Features

- CSV upload validation with filename and size checks
- Canonical schema mapping for common employee column names
- Coercion and validation for salary and required identifiers
- Average salary and department summary calculations
- Threshold-based employee filtering
- Safe CSV export with formula-neutralization
- Controlled API error messages without leaking filesystem details

## Prerequisites

- Python 3.12+
- A local virtual environment
- Access to the project repository

## Setup

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Then open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/docs

## API endpoints

### POST /api/upload

Uploads a CSV file for validation.

Required input:
- multipart form file field called `file`

Returns:
- status
- filename
- valid_rows
- invalid_rows
- message

### POST /api/analyze

Validates the CSV and computes aggregate analysis.

Required form data:
- `file`
- `threshold` (numeric string)
- `include_equal` (`true` or `false`)

Returns:
- average_salary
- employees_included
- department_counts
- matching_employees
- threshold

### POST /api/export

Filters employees and creates a safe CSV export in the managed exports directory.

Required form data:
- `file`
- `threshold`
- `include_equal`
- `filename` (optional, defaults to `filtered.csv`)

Returns:
- filename
- records_exported
- path

## Canonical dataset schema

The project uses a schema-mapping layer rather than assuming one fixed Kaggle header layout. The canonical target schema is:

- `employee_id`
- `name`
- `department`
- `salary`
- `joining_date` (optional)

The loader recognizes common aliases such as:

- employee_id: `employee_id`, `Employee ID`, `employeeid`, `emp_id`
- name: `name`, `employee_name`, `Employee Name`
- department: `department`, `Department`
- salary: `salary`, `annual_salary`, `base_salary`, `Salary`
- joining_date: `joining_date`, `date_of_joining`, `Joining Date`

If required columns are missing, the upload is rejected with a descriptive validation error.

## Security controls

The project treats uploaded CSV content as untrusted input.

Key protections include:

- file extension and size enforcement
- safe filename sanitization
- path traversal rejection
- controlled export directory enforcement
- formula-neutralization for spreadsheet payloads
- structured validation summaries instead of silent data loss
- limited API error responses without exposing local filesystem details

## Known limitations

- The actual Kaggle dataset is not present in the workspace, so this project documents the schema and validation assumptions instead of claiming real-world dataset metadata.
- Salary currency assumptions are not confirmed against a real dataset.
- The project is local-first and does not include cloud deployment or a database-backed persistence layer.
- The browser UI remains intentionally lightweight and is designed for API-driven usage and demonstration rather than enterprise-grade dashboards.

## Testing and verification

```bash
python -m pytest -q
python -m ruff check .
```

Current verified status:

- Full pytest suite passes
- Ruff lint checks pass
- Only dependency deprecation warnings remain from FastAPI/Starlette tooling, not application failures

## Repository hygiene

The project intentionally keeps planning and documentation files outside version control for this local-first portfolio workflow. Files such as PRD.md and the docs directory are excluded from Git tracking in the repo configuration.

## Final note

This project is ready for handoff, portfolio demonstration, and future extension with a real employee dataset once that source becomes available.
