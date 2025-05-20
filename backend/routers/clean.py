from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd
import os
from tempfile import gettempdir
from sklearn.ensemble import IsolationForest

router = APIRouter()

UPLOAD_DIR = os.path.join(gettempdir(), "uploads")

@router.post("/clean")
def clean(
    file_id: str = Query(...),
    impute: str = Query("mean", enum=["mean", "median", "mode"]),
    outlier: bool = Query(True),
    dedupe: bool = Query(True)
):
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
    before = df.head(5).to_dict(orient="records")
    # Imputation
    for col in df.select_dtypes(include=["number", "object"]):
        if df[col].isnull().any():
            if impute == "mean" and df[col].dtype != "O":
                df[col].fillna(df[col].mean(), inplace=True)
            elif impute == "median" and df[col].dtype != "O":
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode().iloc[0], inplace=True)
    # Outlier removal
    outlier_rows = []
    if outlier:
        num_cols = df.select_dtypes(include=["number"]).columns
        if len(num_cols) > 0:
            iso = IsolationForest(contamination=0.05, random_state=42)
            preds = iso.fit_predict(df[num_cols].fillna(0))
            outlier_rows = df.index[preds == -1].tolist()
            df = df[preds != -1]
    # Duplicates
    dup_rows = []
    if dedupe:
        dup_rows = df[df.duplicated()].index.tolist()
        df = df.drop_duplicates()
    after = df.head(5).to_dict(orient="records")
    summary = {
        "imputation": impute,
        "outliers_removed": len(outlier_rows),
        "duplicates_removed": len(dup_rows)
    }
    # Save cleaned file for download
    cleaned_path = os.path.join(UPLOAD_DIR, f"{file_id}_cleaned.csv")
    df.to_csv(cleaned_path, index=False)
    return JSONResponse({"before": before, "after": after, "summary": summary, "cleaned_file_id": f"{file_id}_cleaned"}) 