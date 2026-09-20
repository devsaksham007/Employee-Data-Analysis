from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"
TEMP_DIR = BASE_DIR / ".tmp"

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSION = ".csv"

DEFAULT_SCHEMA_MAPPING = {
    "employee_id": ["employee_id", "employeeid", "emp_id", "Employee ID"],
    "name": ["name", "employee_name", "Employee Name"],
    "department": ["department", "Department"],
    "salary": ["salary", "annual_salary", "base_salary", "Salary"],
    "joining_date": ["joining_date", "date_of_joining", "Joining Date"],
}
