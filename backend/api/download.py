from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import FileResponse
import os
from utils.auth import verify_token

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data/cleaned')

@router.get("/download/{session_id}")
async def download(request: Request, session_id: str = Path(...)):
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth.split()[1]
    verify_token(token)
    file_path = os.path.join(DATA_DIR, f"{session_id}_cleaned.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(file_path, media_type="text/csv", filename=f"{session_id}_cleaned.csv") 