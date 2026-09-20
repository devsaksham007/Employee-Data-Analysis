from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse

from app.core.config import ALLOWED_EXTENSION
from app.core.security import sanitize_filename
from app.services.csv_loader import CSVLoader, CSVValidationError

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
