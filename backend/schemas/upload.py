from pydantic import BaseModel
from typing import List, Any

class UploadResponse(BaseModel):
    session_id: str
    preview: List[Any]
    columns: List[str] 