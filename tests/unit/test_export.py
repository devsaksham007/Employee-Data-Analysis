from pathlib import Path

import pandas as pd

from app.services.export import CSVExporter, ExportValidationError


def test_export_dataframe_writes_safe_csv(tmp_path: Path) -> None:
    exporter = CSVExporter(export_root=tmp_path)
    df = pd.DataFrame(
        {
            "employee_id": ["EMP001"],
            "name": ["=HYPERLINK(\"https://example.com\")"],
            "department": ["Engineering"],
            "salary": [75000.0],
        }
    )

    target = exporter.export_dataframe(
        df,
        "filtered.csv",
        ["employee_id", "name", "department", "salary"],
    )

    assert target.exists()
    contents = target.read_text(encoding="utf-8")
    assert "'=HYPERLINK" in contents
    assert "https://example.com" in contents


def test_export_dataframe_rejects_untrusted_output_path(tmp_path: Path) -> None:
    exporter = CSVExporter(export_root=tmp_path)
    df = pd.DataFrame({"employee_id": ["EMP001"], "salary": [75000.0]})

    try:
        exporter.export_dataframe(df, "../outside.csv")
        raise AssertionError("Expected ExportValidationError")
    except ExportValidationError:
        pass
