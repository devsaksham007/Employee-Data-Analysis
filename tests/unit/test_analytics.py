import pandas as pd

from app.services.analytics import EmployeeAnalytics


def test_average_salary_uses_valid_salary_values() -> None:
    df = pd.DataFrame(
        {
            "employee_id": ["EMP001", "EMP002", "EMP003"],
            "name": ["Alice", "Bob", "Cara"],
            "department": ["Engineering", "HR", "Engineering"],
            "salary": [75000, 68000, 90000],
        }
    )

    result = EmployeeAnalytics().average_salary(df)

    assert result == 77666.66666666667


def test_department_counts_are_grouped_and_normalized() -> None:
    df = pd.DataFrame(
        {
            "employee_id": ["EMP001", "EMP002", "EMP003"],
            "name": ["Alice", "Bob", "Cara"],
            "department": ["Engineering", " engineering ", "Hr"],
            "salary": [75000, 68000, 90000],
        }
    )

    result = EmployeeAnalytics().department_counts(df)

    assert result["department"].tolist() == ["Engineering", "Hr"]
    assert result["employee_count"].tolist() == [2, 1]


def test_filter_by_salary_honors_threshold_definition() -> None:
    df = pd.DataFrame(
        {
            "employee_id": ["EMP001", "EMP002", "EMP003"],
            "name": ["Alice", "Bob", "Cara"],
            "department": ["Engineering", "HR", "Engineering"],
            "salary": [75000, 68000, 90000],
        }
    )

    result = EmployeeAnalytics().filter_by_salary(df, 75000)
    result_with_equal = EmployeeAnalytics().filter_by_salary(df, 75000, include_equal=True)

    assert len(result) == 1
    assert result["employee_id"].tolist() == ["EMP003"]
    assert len(result_with_equal) == 2
    assert result_with_equal["employee_id"].tolist() == ["EMP001", "EMP003"]
