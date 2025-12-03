from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: str
    language: Optional[str] = None  # 'en', 'ar', or auto-detect if None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    category: str
    language: str
    resolved: bool

class FeedbackRequest(BaseModel):
    session_id: str
    feedback_type: str  # 'like' or 'dislike'
    comment: Optional[str] = None

class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    file_size: int
    indexed_at: datetime
    chunk_count: int
