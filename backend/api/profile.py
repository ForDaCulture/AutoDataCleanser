from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import JSONResponse
import pandas as pd
import os
from utils.cleaning import profile_data
from utils.auth import verify_token

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data/cleaned')

@router.get("/profile/{session_id}")
async def profile(request: Request, session_id: str = Path(...)):
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth.split()[1]
    verify_token(token)
    file_path = None
    for ext in [".csv", ".xlsx", ".xls"]:
        candidate = os.path.join(DATA_DIR, f"{session_id}{ext}")
        if os.path.exists(candidate):
            file_path = candidate
            break
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found.")
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    return {"success": True, **profile_data(df)} 