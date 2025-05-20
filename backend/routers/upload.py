from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
import uuid
from tempfile import gettempdir

router = APIRouter()

UPLOAD_DIR = os.path.join(gettempdir(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_csv")
def upload_csv(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    if ext == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    preview = df.head(5).to_dict(orient="records")
    return JSONResponse({"file_id": file_id, "preview": preview, "columns": list(df.columns)}) 