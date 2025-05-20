from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import pandas as pd
import os
import uuid
from db.supabase_client import supabase
from utils.auth import verify_jwt
from utils.audit import log_action

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), '../data/uploads')
os.makedirs(DATA_DIR, exist_ok=True)

@router.post("/upload")
async def upload(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Depends(verify_jwt)
):
    try:
        # Validate file type
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".csv", ".xlsx", ".xls"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload a CSV or Excel file."
            )

        # Generate session ID and save file
        session_id = str(uuid.uuid4())
        file_path = os.path.join(DATA_DIR, f"{session_id}{ext}")
        
        # Read and validate file content
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
            
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)

        # Read data for preview
        try:
            if ext == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            os.remove(file_path)  # Clean up invalid file
            raise HTTPException(
                status_code=400,
                detail=f"Error reading file: {str(e)}"
            )

        # Create cleaning session record
        try:
            supabase.table("cleaning_sessions").insert({
                "id": session_id,
                "user_id": user_id,
                "original_filename": file.filename,
                "cleaned_filename": None,
                "rows_cleaned": None,
                "summary": None,
                "status": "uploaded"
            }).execute()
        except Exception as e:
            os.remove(file_path)  # Clean up file if DB insert fails
            raise HTTPException(
                status_code=500,
                detail="Failed to create cleaning session"
            )

        # Log the action
        log_action(user_id, "upload", {
            "session_id": session_id,
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns)
        })

        return {
            "success": True,
            "session_id": session_id,
            "preview": df.head(5).to_dict(orient="records"),
            "columns": list(df.columns),
            "rows": len(df)
        }

    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if something unexpected happens
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        ) 