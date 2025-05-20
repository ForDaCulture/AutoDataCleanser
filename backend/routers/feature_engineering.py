from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd
import os
from tempfile import gettempdir

router = APIRouter()

UPLOAD_DIR = os.path.join(gettempdir(), "uploads")

@router.get("/feature_engineering")
def feature_engineering(file_id: str = Query(...)):
    file_path = None
    for ext in [".csv", ".xlsx", ".xls"]:
        candidate = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
        if os.path.exists(candidate):
            file_path = candidate
            break
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found.")
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    suggestions = []
    # Date parting
    for col in df.select_dtypes(include=["datetime", "object"]):
        try:
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notnull().any():
                suggestions.append({"column": col, "type": "date_parting", "parts": ["year", "month", "day", "weekday"]})
        except Exception:
            continue
    # Ratios
    num_cols = df.select_dtypes(include=["number"]).columns
    if len(num_cols) >= 2:
        for i, col1 in enumerate(num_cols):
            for col2 in num_cols[i+1:]:
                suggestions.append({"type": "ratio", "columns": [col1, col2]})
    # One-hot encoding
    for col in df.select_dtypes(include=["object", "category"]):
        if df[col].nunique() < 20:
            suggestions.append({"column": col, "type": "one_hot"})
    return JSONResponse({"suggestions": suggestions}) 