# Employee Data Analysis

A secure, local-first employee CSV analysis application built with Python, FastAPI, and Pandas.

## Overview

This project is designed to ingest employee CSV data, validate records, calculate salary statistics, filter by threshold, and export safe CSV results.

## Local setup

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

## Run the app

```bash
uvicorn app.main:app --reload
```

## Testing

```bash
python -m pytest -q
```

## Notes

- The Kaggle dataset has not been added to the workspace yet.
- The project uses a schema mapping strategy and will validate the real dataset when available.
