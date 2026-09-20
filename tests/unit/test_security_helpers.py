from app.core.security import is_formula_like, sanitize_filename


def test_sanitize_filename_rejects_paths() -> None:
    result = sanitize_filename("../../etc/passwd.csv")
    assert result == "upload.csv"


def test_is_formula_like_detects_spreadsheet_payloads() -> None:
    assert is_formula_like("=HYPERLINK(\"https://example.com\")") is True
    assert is_formula_like("+123") is True
    assert is_formula_like("-10") is True
    assert is_formula_like("@SUM(A1:A2)") is True
    assert is_formula_like("Jane Doe") is False
