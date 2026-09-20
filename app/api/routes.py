from fastapi import APIRouter, Form, UploadFile
from fastapi.responses import JSONResponse

from app.core.config import ALLOWED_EXTENSION
from app.core.security import sanitize_filename
from app.services.analytics import EmployeeAnalytics
from app.services.csv_loader import CSVLoader, CSVValidationError
from app.services.export import CSVExporter, ExportValidationError

router = APIRouter(prefix="/api", tags=["employee-data"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/upload", response_model=None)
async def upload_employee_csv(file: UploadFile) -> dict[str, object] | JSONResponse:
    if file.filename is None:
        return JSONResponse(status_code=400, content={"status": "error", "message": "A CSV file is required."})

    if not file.filename.lower().endswith(ALLOWED_EXTENSION):
        return JSONResponse(status_code=400, content={"status": "error", "message": "Only CSV files are allowed."})

    try:
        file_bytes = await file.read()
        result = CSVLoader().load_from_bytes(file_bytes, file.filename)
    except CSVValidationError as exc:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(exc)})

    safe_filename = sanitize_filename(file.filename)
    return {
        "status": "accepted",
        "filename": safe_filename,
        "valid_rows": result.validation_summary.valid_rows,
        "invalid_rows": result.validation_summary.invalid_rows,
        "message": "CSV file passed validation.",
    }


@router.post("/analyze", response_model=None)
async def analyze_employee_csv(
    file: UploadFile,
    threshold: str = Form(...),
    include_equal: str = Form("false"),
) -> dict[str, object] | JSONResponse:
    if file.filename is None:
        return JSONResponse(status_code=400, content={"status": "error", "message": "A CSV file is required."})

    try:
        threshold_value = float(threshold)
    except ValueError:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Threshold must be numeric."})

    try:
        file_bytes = await file.read()
        result = CSVLoader().load_from_bytes(file_bytes, file.filename)
    except CSVValidationError as exc:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(exc)})

    analytics = EmployeeAnalytics()
    filtered = analytics.filter_by_salary(result.df, threshold_value, include_equal=(include_equal.lower() == "true"))
    department_counts = analytics.department_counts(result.df)

    return {
        "status": "success",
        "average_salary": analytics.average_salary(result.df),
        "employees_included": int(result.validation_summary.valid_rows),
        "department_counts": department_counts.to_dict(orient="records"),
        "matching_employees": int(len(filtered)),
        "threshold": threshold_value,
    }


@router.post("/export", response_model=None)
async def export_employee_csv(
    file: UploadFile,
    threshold: str = Form(...),
    include_equal: str = Form("false"),
    filename: str = Form("filtered.csv"),
) -> dict[str, object] | JSONResponse:
    if file.filename is None:
        return JSONResponse(status_code=400, content={"status": "error", "message": "A CSV file is required."})

    try:
        threshold_value = float(threshold)
    except ValueError:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Threshold must be numeric."})

    try:
        file_bytes = await file.read()
        result = CSVLoader().load_from_bytes(file_bytes, file.filename)
        analytics = EmployeeAnalytics()
        filtered = analytics.filter_by_salary(result.df, threshold_value, include_equal=(include_equal.lower() == "true"))
        exporter = CSVExporter()
        output_path = exporter.export_dataframe(filtered, filename, ["employee_id", "name", "department", "salary"])
    except (CSVValidationError, ExportValidationError) as exc:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(exc)})

    return {
        "status": "success",
        "filename": output_path.name,
        "records_exported": int(len(filtered)),
        "path": str(output_path),
    }
