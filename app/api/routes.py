from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/api", tags=["employee-data"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/upload")
async def upload_employee_csv(file: UploadFile) -> dict[str, str]:
    if file.filename is None:
        return {"status": "error", "message": "A CSV file is required."}

    if not file.filename.lower().endswith(".csv"):
        return {"status": "error", "message": "Only CSV files are allowed."}

    return {
        "status": "accepted",
        "filename": file.filename,
        "message": "Upload endpoint ready for Phase 3 implementation.",
    }
