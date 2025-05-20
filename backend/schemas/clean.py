from pydantic import BaseModel
from typing import List, Any, Optional

class CleanRequest(BaseModel):
    session_id: str
    impute: str = "mean"
    outlier: bool = True
    dedupe: bool = True

class CleanResponse(BaseModel):
    summary: dict
    before: List[Any]
    after: List[Any] 