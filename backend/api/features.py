from fastapi import APIRouter, HTTPException, Request, Body
import pandas as pd
import os
from utils.cleaning import suggest_features
from utils.auth import verify_token

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data/cleaned')

@router.post("/features")
async def features(request: Request, body: dict = Body(...)):
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth.split()[1]
    verify_token(token)
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id")
    file_path = os.path.join(DATA_DIR, f"{session_id}_cleaned.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    df = pd.read_csv(file_path)
    return {"success": True, **suggest_features(df)} 