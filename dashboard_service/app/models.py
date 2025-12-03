from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class DashboardMetrics(BaseModel):
    total_chats: int
    resolved_chats: int
    unresolved_chats: int
    resolution_rate: float
    avg_response_time: float
    positive_feedback: int
    negative_feedback: int
    feedback_rate: float

class ChatAnalytics(BaseModel):
    categories: Dict[str, int]
    languages: Dict[str, int]
    daily_chats: Dict[str, int]
    confidence_distribution: Dict[str, int]

class SentimentAnalysis(BaseModel):
    sentiment_counts: Dict[str, int]
    sentiment_percentages: Dict[str, float]
    total_analyzed: int

class SupportQueueItem(BaseModel):
    id: str
    user_id: Optional[str]
    session_id: str
    message: str
    response: str
    category: str
    confidence: float
    timestamp: datetime
    status: str
    feedback_comment: Optional[str] = None

class RecentChat(BaseModel):
    id: str
    user_id: Optional[str]
    session_id: str
    message: str
    response: str
    language: str
    category: str
    confidence: float
    resolved: bool
    timestamp: datetime
    feedback_type: Optional[str] = None
    feedback_comment: Optional[str] = None
