from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


def test_analyze_endpoint_returns_summary_metrics() -> None:
    client = TestClient(app)
    content = (
        b"Employee ID,Name,Department,Salary\n"
        b"EMP001,Alice,Engineering,75000\n"
        b"EMP002,Bob,HR,68000\n"
        b"EMP003,Cara,Engineering,90000\n"
    )

    response = client.post(
        "/api/analyze",
        files={"file": ("employees.csv", BytesIO(content), "text/csv")},
        data={"threshold": "70000", "include_equal": "false"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["average_salary"] == 77666.66666666667
    assert payload["employees_included"] == 3
    assert payload["department_counts"][0]["department"] == "Engineering"
    assert payload["matching_employees"] == 2


def test_export_endpoint_creates_a_csv_file() -> None:
    client = TestClient(app)
    content = (
        b"Employee ID,Name,Department,Salary\n"
        b"EMP001,Alice,Engineering,75000\n"
        b"EMP002,Bob,HR,68000\n"
        b"EMP003,Cara,Engineering,90000\n"
    )

    response = client.post(
        "/api/export",
        files={"file": ("employees.csv", BytesIO(content), "text/csv")},
        data={"threshold": "70000", "include_equal": "false", "filename": "filtered.csv"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["filename"].endswith("filtered.csv")
