from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from supabase import create_client, Client
import os
import json

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

@router.post("/audit_log")
def store_audit_log(session_id: str = Query(...), log: dict = Body(...)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured.")
    data = {"session_id": session_id, "log": json.dumps(log)}
    res = supabase.table("audit_logs").insert(data).execute()
    if res.get("status_code") != 201:
        raise HTTPException(status_code=500, detail="Failed to store audit log.")
    return {"status": "success"}

@router.get("/audit_log")
def get_audit_log(session_id: str = Query(...)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured.")
    res = supabase.table("audit_logs").select("log").eq("session_id", session_id).execute()
    logs = [json.loads(r["log"]) for r in res.data] if res.data else []
    return JSONResponse({"logs": logs}) 