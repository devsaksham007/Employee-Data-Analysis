from __future__ import annotations

from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """Return a safe filesystem name without using user-controlled paths."""
    unsafe = Path(filename).name
    stem = Path(unsafe).stem
    suffix = Path(unsafe).suffix.lower()
    safe_stem = "upload" if not stem else "".join(ch for ch in stem if ch.isalnum() or ch in {"-", "_"})
    safe_suffix = suffix if suffix in {".csv"} else ".csv"
    return f"{safe_stem or 'upload'}{safe_suffix}"


def is_formula_like(value: str) -> bool:
    striped = value.lstrip()
    return striped.startswith(("=", "+", "-", "@"))
