import os
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api import upload, profile, clean, audit, download, features, auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    print(f"Exception: {exc}")
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"success": False, "error": "Internal server error"})

app.include_router(auth.router)
app.include_router(upload.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(clean.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(download.router, prefix="/api")
app.include_router(features.router, prefix="/api") 