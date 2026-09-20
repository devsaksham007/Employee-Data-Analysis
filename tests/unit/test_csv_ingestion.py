from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.csv_loader import CSVLoader, CSVValidationError


@pytest.fixture
def valid_csv_bytes() -> bytes:
    return (
        b"Employee ID,Name,Department,Salary\n"
        b"EMP001,Alice,Engineering,75000\n"
        b"EMP002,Bob,HR,68000\n"
        b"EMP003,Carol,Engineering,90000\n"
    )


def test_csv_loader_accepts_valid_csv(valid_csv_bytes: bytes) -> None:
    loader = CSVLoader()
    result = loader.load_from_bytes(valid_csv_bytes, "employees.csv")

    assert result.validation_summary.total_rows == 3
    assert result.validation_summary.valid_rows == 3
    assert result.validation_summary.invalid_rows == 0
    assert result.df["salary"].tolist() == [75000.0, 68000.0, 90000.0]


def test_csv_loader_rejects_missing_required_columns() -> None:
    loader = CSVLoader()
    csv_bytes = b"Employee ID,Name,Department\nEMP001,Alice,Engineering\n"

    with pytest.raises(CSVValidationError, match="Missing required columns"):
        loader.load_from_bytes(csv_bytes, "employees.csv")


def test_csv_loader_reports_invalid_salary_values() -> None:
    loader = CSVLoader()
    csv_bytes = (
        b"Employee ID,Name,Department,Salary\n"
        b"EMP001,Alice,Engineering,75000\n"
        b"EMP002,Bob,HR,not-a-number\n"
    )

    result = loader.load_from_bytes(csv_bytes, "employees.csv")

    assert result.validation_summary.total_rows == 2
    assert result.validation_summary.valid_rows == 1
    assert result.validation_summary.invalid_rows == 1
    assert result.validation_summary.missing_salary == 0


def test_csv_loader_rejects_oversized_file() -> None:
    loader = CSVLoader(max_file_size_bytes=10)
    payload = b"Employee ID,Name,Department,Salary\nEMP001,Alice,Engineering,75000\n"

    with pytest.raises(CSVValidationError, match="exceeds the maximum allowed size"):
        loader.load_from_bytes(payload, "employees.csv")


def test_upload_endpoint_validates_csv_content() -> None:
    client = TestClient(app)
    content = b"Employee ID,Name,Department,Salary\nEMP001,Alice,Engineering,75000\n"

    response = client.post(
        "/api/upload",
        files={"file": ("employees.csv", BytesIO(content), "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "accepted"
    assert payload["valid_rows"] == 1
    assert payload["invalid_rows"] == 0


def test_upload_endpoint_rejects_missing_salary_column() -> None:
    client = TestClient(app)
    content = b"Employee ID,Name,Department\nEMP001,Alice,Engineering\n"

    response = client.post(
        "/api/upload",
        files={"file": ("employees.csv", BytesIO(content), "text/csv")},
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["status"] == "error"
    assert "Missing required columns" in payload["message"]
