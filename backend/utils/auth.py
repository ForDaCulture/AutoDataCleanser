from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
import os
from typing import Optional

def verify_token(token: str) -> str:
    """
    Verify a Supabase JWT token and return the user ID.
    Raises HTTPException if token is invalid.
    """
    try:
        payload = jwt.decode(token, os.getenv("SUPABASE_JWT_SECRET"), algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_jwt(request: Request) -> str:
    """
    Extract and verify JWT from request headers.
    Returns the user ID if valid.
    """
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.split()[1]
    return verify_token(token)

def get_user_id(payload: str = Depends(verify_jwt)) -> str:
    """
    Dependency to get user ID from verified JWT.
    """
    return payload 