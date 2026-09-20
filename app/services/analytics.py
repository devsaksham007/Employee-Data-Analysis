from __future__ import annotations

import pandas as pd


class EmployeeAnalytics:
    def average_salary(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0

        numeric_salary = pd.to_numeric(df["salary"], errors="coerce")
        valid = numeric_salary.dropna()
        if valid.empty:
            return 0.0

        return float(valid.mean())

    def department_counts(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["department", "employee_count"])

        counts = (
            df.assign(department=df["department"].astype("string").str.strip().str.title())
            .groupby("department", dropna=False)
            .size()
            .reset_index(name="employee_count")
        )
        counts.columns = ["department", "employee_count"]
        return counts

    def filter_by_salary(self, df: pd.DataFrame, threshold: float, include_equal: bool = False) -> pd.DataFrame:
        if df.empty:
            return df.copy()

        numeric_salary = pd.to_numeric(df["salary"], errors="coerce")
        filtered = df.loc[numeric_salary.notna()].copy()

        if filtered.empty:
            return filtered

        if include_equal:
            filtered = filtered.loc[numeric_salary.loc[filtered.index] >= threshold].copy()
        else:
            filtered = filtered.loc[numeric_salary.loc[filtered.index] > threshold].copy()

        return filtered
