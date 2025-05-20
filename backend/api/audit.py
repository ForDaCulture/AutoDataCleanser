from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import JSONResponse
from db.supabase_client import supabase
from utils.auth import verify_token

router = APIRouter()

@router.get("/audit/{session_id}")
async def get_audit(request: Request, session_id: str = Path(...)):
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth.split()[1]
    verify_token(token)
    res = supabase.table("audit_logs").select("*").contains("details", {"session_id": session_id}).order("created_at").execute()
    logs = res.data if res.data else []
    return {"success": True, "logs": logs} 