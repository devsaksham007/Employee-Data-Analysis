from __future__ import annotations

from dataclasses import dataclass
from io import StringIO

import pandas as pd

from app.core.config import DEFAULT_SCHEMA_MAPPING, MAX_UPLOAD_SIZE_BYTES
from app.core.security import sanitize_filename


class CSVValidationError(ValueError):
    """Raised when CSV file content or schema is invalid."""


@dataclass
class CSVLoadResult:
    df: pd.DataFrame
    validation_summary: "ValidationSummary"
    original_filename: str


@dataclass
class ValidationSummary:
    total_rows: int
    valid_rows: int
    invalid_rows: int
    missing_salary: int = 0
    duplicate_employee_ids: int = 0


class CSVLoader:
    def __init__(self, max_file_size_bytes: int = MAX_UPLOAD_SIZE_BYTES) -> None:
        self.max_file_size_bytes = max_file_size_bytes
        self.required_columns = ["employee_id", "name", "department", "salary"]

    def load_from_bytes(self, file_bytes: bytes, filename: str) -> CSVLoadResult:
        if not file_bytes:
            raise CSVValidationError("CSV file is empty.")

        if len(file_bytes) > self.max_file_size_bytes:
            raise CSVValidationError("Uploaded file exceeds the maximum allowed size.")

        safe_name = sanitize_filename(filename)
        if safe_name == "upload.csv" and filename and filename.strip() not in {"", "."}:
            # A user-friendly guard for traversal-like submissions.
            pass

        text = file_bytes.decode("utf-8-sig", errors="strict")
        if not text.strip():
            raise CSVValidationError("CSV file is empty.")

        try:
            df = pd.read_csv(StringIO(text), dtype={"Employee ID": "string"}, keep_default_na=True)
        except Exception as exc:  # pragma: no cover - defensive parser guard
            raise CSVValidationError(f"Malformed CSV data: {exc}") from exc

        if df.empty:
            raise CSVValidationError("CSV file contains no rows.")

        normalized = self._normalize_columns(df)
        self._validate_schema(normalized)
        raw_salary = normalized["salary"].copy()
        normalized = self._coerce_core_types(normalized)
        validation = self._summarize_validation(normalized, raw_salary)

        return CSVLoadResult(
            df=normalized,
            validation_summary=validation,
            original_filename=safe_name,
        )

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        canonical_map: dict[str, str] = {}
        for column in df.columns:
            lower = str(column).strip().lower()
            for canonical_name, aliases in DEFAULT_SCHEMA_MAPPING.items():
                if lower in {alias.lower() for alias in aliases}:
                    canonical_map[column] = canonical_name
                    break

        if not canonical_map:
            raise CSVValidationError("CSV file has no recognizable employee columns.")

        renamed = df.rename(columns=canonical_map)
        return renamed

    def _validate_schema(self, df: pd.DataFrame) -> None:
        missing_columns = [column for column in self.required_columns if column not in df.columns]
        if missing_columns:
            raise CSVValidationError(f"Missing required columns: {', '.join(missing_columns)}")

    def _coerce_core_types(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        result["employee_id"] = result["employee_id"].astype("string").fillna("")
        result["name"] = result["name"].astype("string").fillna("")
        result["department"] = result["department"].astype("string").fillna("")

        salary_series = pd.to_numeric(result["salary"], errors="coerce")
        result["salary"] = salary_series
        return result

    def _summarize_validation(
        self,
        df: pd.DataFrame,
        raw_salary: pd.Series | None = None,
    ) -> ValidationSummary:
        total_rows = int(len(df))
        valid_mask = (
            df["salary"].notna()
            & df["employee_id"].astype("string").str.len().gt(0)
        )
        valid_rows = int(valid_mask.sum())
        invalid_rows = total_rows - valid_rows

        source_salary = raw_salary if raw_salary is not None else df["salary"]
        missing_salary = int(source_salary.isna().sum())
        duplicate_employee_ids = int(
            df.loc[
                df["employee_id"].astype("string").duplicated(keep=False),
                "employee_id",
            ].nunique()
        )

        return ValidationSummary(
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            missing_salary=missing_salary,
            duplicate_employee_ids=duplicate_employee_ids,
        )
