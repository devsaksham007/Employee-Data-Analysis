from __future__ import annotations

from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """Return a safe filesystem name without using user-controlled paths."""
    candidate = str(filename or "").strip()
    if not candidate or candidate in {".", ".."}:
        return "upload.csv"

    normalized = Path(candidate)
    name = normalized.name
    if not name or name in {".", ".."} or "/" in candidate or "\\" in candidate:
        return "upload.csv"

    stem = Path(name).stem
    suffix = Path(name).suffix.lower()

    if not stem or stem in {".", ".."}:
        return "upload.csv"

    safe_stem = "".join(ch for ch in stem if ch.isalnum() or ch in {"-", "_"})
    if not safe_stem:
        return "upload.csv"

    safe_suffix = suffix if suffix in {".csv"} else ".csv"
    return f"{safe_stem}{safe_suffix}"


def is_formula_like(value: str) -> bool:
    striped = value.lstrip()
    return striped.startswith(("=", "+", "-", "@"))
