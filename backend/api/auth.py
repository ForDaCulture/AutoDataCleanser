from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from backend.db.supabase_client import get_supabase_client

router = APIRouter(prefix="/api/auth", tags=["auth"])

class AuthPayload(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
async def signup(payload: AuthPayload):
    try:
        supabase = get_supabase_client()
        resp = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password
        })
        if resp.user is None:
            raise HTTPException(status_code=400, detail=resp.error.message)
        return {"user": resp.user, "session": resp.session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signin")
async def signin(payload: AuthPayload):
    try:
        supabase = get_supabase_client()
        resp = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password
        })
        if resp.session is None:
            raise HTTPException(status_code=400, detail=resp.error.message)
        return {"access_token": resp.session.access_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 