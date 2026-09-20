from __future__ import annotations

from pydantic import BaseModel, Field


class EmployeeRecord(BaseModel):
    employee_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1)
    salary: float = Field(..., gt=0)
    joining_date: str | None = None


class ValidationSummary(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    missing_salary: int = 0
    duplicate_employee_ids: int = 0
