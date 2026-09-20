from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.config import EXPORT_DIR
from app.core.security import is_formula_like


class ExportValidationError(ValueError):
    """Raised when export parameters are invalid or unsafe."""


class CSVExporter:
    def __init__(self, export_root: str | Path | None = None) -> None:
        self.export_root = Path(export_root) if export_root is not None else EXPORT_DIR
        self.export_root.mkdir(parents=True, exist_ok=True)

    def sanitize_value(self, value: object) -> object:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""

        text = str(value)
        if is_formula_like(text):
            return "'" + text
        return text

    def export_dataframe(
        self,
        df: pd.DataFrame,
        filename: str,
        include_columns: list[str] | None = None,
    ) -> Path:
        if not filename or not filename.strip():
            raise ExportValidationError("Export filename is required.")

        if ".." in Path(filename).parts or "/" in filename or "\\" in filename:
            raise ExportValidationError("Export path is outside the allowed directory.")

        safe_name = Path(filename).name
        if not safe_name.lower().endswith(".csv"):
            safe_name = f"{safe_name}.csv"

        candidate = self.export_root / safe_name
        target_path = candidate.resolve()
        allowed_root = self.export_root.resolve()
        try:
            target_path.relative_to(allowed_root)
        except ValueError as exc:
            raise ExportValidationError(
                "Export path is outside the allowed directory."
            ) from exc

        export_df = df.copy()
        if include_columns is not None:
            export_df = export_df.loc[
                :,
                [column for column in include_columns if column in export_df.columns],
            ]

        safe_export = export_df.copy()
        for column in safe_export.columns:
            safe_export[column] = safe_export[column].map(self.sanitize_value)

        safe_export.to_csv(target_path, index=False)
        return target_path
