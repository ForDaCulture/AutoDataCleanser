from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd
import os
from tempfile import gettempdir

router = APIRouter()

UPLOAD_DIR = os.path.join(gettempdir(), "uploads")

@router.get("/profile")
def profile(file_id: str = Query(...)):
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
    stats = []
    for col in df.columns:
        col_data = df[col]
        stats.append({
            "column": col,
            "type": str(col_data.dtype),
            "missing_pct": float(col_data.isnull().mean()) * 100,
            "unique_count": int(col_data.nunique())
        })
    return JSONResponse({"profile": stats}) 