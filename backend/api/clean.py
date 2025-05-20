from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse
import pandas as pd
import os
from utils.cleaning import auto_clean
from utils.auth import verify_token
from utils.audit import log_action
from db.supabase_client import supabase

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data/cleaned')

@router.post("/clean")
async def clean(request: Request, body: dict = Body(...)):
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth.split()[1]
    user_id = verify_token(token)
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id")
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
    cleaned, summary = auto_clean(df)
    cleaned_path = os.path.join(DATA_DIR, f"{session_id}_cleaned.csv")
    cleaned.to_csv(cleaned_path, index=False)
    # Update cleaning_sessions
    supabase.table("cleaning_sessions").update({
        "cleaned_filename": f"{session_id}_cleaned.csv",
        "rows_cleaned": len(cleaned),
        "summary": summary
    }).eq("id", session_id).execute()
    log_action(user_id, "clean", {"session_id": session_id, "summary": summary})
    return {
        "success": True,
        "summary": summary,
        "before": df.head(5).to_dict(orient="records"),
        "after": cleaned.head(5).to_dict(orient="records")
    } 