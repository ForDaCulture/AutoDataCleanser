from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import os
from tempfile import gettempdir

router = APIRouter()

UPLOAD_DIR = os.path.join(gettempdir(), "uploads")

@router.get("/download")
def download(file_id: str = Query(...)):
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(file_path, media_type="text/csv", filename=f"{file_id}.csv") 