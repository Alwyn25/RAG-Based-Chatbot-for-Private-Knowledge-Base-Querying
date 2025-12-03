from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
from collections import defaultdict

from .models import DashboardMetrics, ChatAnalytics, SentimentAnalysis

router = APIRouter(prefix="/api")

# Mock data for demonstration purposes
# In production, this would connect to the same data source as the chatbot service
sample_chat_logs = [
    {
        "user_id": "user_123",
        "session_id": "session_456",
        "message": "How do I reset my password?",
        "response": "To reset your password, go to login page and click 'Forgot Password'",
        "language": "en",
        "category": "Transactional",
        "confidence": 0.85,
        "timestamp": "2024-12-23T10:30:00",
        "resolved": True,
        "feedback_type": "like"
    },
    {
        "user_id": "user_789",
        "session_id": "session_101",
        "message": "App keeps crashing",
        "response": "Please try restarting the app and updating to the latest version",
        "language": "en",
        "category": "Tech issue",
        "confidence": 0.72,
        "timestamp": "2024-12-23T11:15:00",
        "resolved": True,
        "feedback_type": "like"
    },
    {
        "user_id": "user_456",
        "session_id": "session_202",
        "message": "What are your business hours?",
        "response": "Our support is available Monday to Friday 9 AM to 6 PM EST",
        "language": "en",
        "category": "Product FAQ",
        "confidence": 0.95,
        "timestamp": "2024-12-23T12:00:00",
        "resolved": True
    }
]

# Initialize sentiment analyzer
# Note: Transformers dependency disabled for now due to compatibility issues
# try:
#     from transformers import pipeline
#     sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
# except Exception as e:
#     print(f"Warning: Could not load sentiment analyzer: {e}")
sentiment_analyzer = None

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """Get overall dashboard metrics"""
    try:
        # Filter sample data based on query parameters
        filtered_logs = sample_chat_logs.copy()
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.get("user_id") == user_id]
        
        # Calculate basic metrics
        total_chats = len(filtered_logs)
        resolved_chats = len([log for log in filtered_logs if log.get("resolved", False)])
        unresolved_chats = total_chats - resolved_chats
        
        # Calculate average response time (simulated)
        avg_response_time = 2.5  # seconds
        
        # Calculate category distribution
        categories = defaultdict(int)
        for log in filtered_logs:
            categories[log.get("category", "unknown")] += 1
        
        # Calculate confidence scores
        confidence_scores = [log.get("confidence", 0.5) for log in filtered_logs]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Calculate feedback metrics
        positive_feedback = len([log for log in filtered_logs if log.get("feedback_type") == "like"])
        negative_feedback = len([log for log in filtered_logs if log.get("feedback_type") == "dislike"])
        feedback_rate = ((positive_feedback + negative_feedback) / total_chats * 100) if total_chats > 0 else 0
        
        return DashboardMetrics(
            total_chats=total_chats,
            resolved_chats=resolved_chats,
            unresolved_chats=unresolved_chats,
            resolution_rate=(resolved_chats / total_chats * 100) if total_chats > 0 else 0,
            avg_response_time=avg_response_time,
            positive_feedback=positive_feedback,
            negative_feedback=negative_feedback,
            feedback_rate=feedback_rate
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/analytics", response_model=ChatAnalytics)
async def get_chat_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get detailed chat analytics"""
    try:
        # Calculate analytics based on sample data
        categories = defaultdict(int)
        languages = defaultdict(int)
        daily_chats = defaultdict(int)
        confidence_distribution = defaultdict(int)
        
        for log in sample_chat_logs:
            categories[log.get("category", "unknown")] += 1
            languages[log.get("language", "en")] += 1
            # Simplified daily grouping
            daily_chats["2024-12-23"] += 1
            # Confidence distribution by ranges
            conf = log.get("confidence", 0.5)
            if conf >= 0.8:
                confidence_distribution["high"] += 1
            elif conf >= 0.5:
                confidence_distribution["medium"] += 1
            else:
                confidence_distribution["low"] += 1
        
        return ChatAnalytics(
            categories=dict(categories),
            languages=dict(languages),
            daily_chats=dict(daily_chats),
            confidence_distribution=dict(confidence_distribution)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/sentiment", response_model=SentimentAnalysis)
async def get_sentiment_analysis():
    """Get sentiment analysis of recent chats"""
    try:
        # Mock sentiment analysis since transformers is not available
        sentiment_counts = {"positive": 2, "neutral": 1, "negative": 0}
        total = sum(sentiment_counts.values())
        sentiment_percentages = {k: (v/total*100) if total > 0 else 0 for k, v in sentiment_counts.items()}
        
        return SentimentAnalysis(
            sentiment_counts=sentiment_counts,
            sentiment_percentages=sentiment_percentages,
            total_analyzed=total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sentiment analysis: {str(e)}")
        avg_response_time = 2.5  # Average response time in seconds
        
        # Get feedback breakdown
        positive_feedback = chat_logs.count_documents({**query_filter, "feedback_type": "like"})
        negative_feedback = chat_logs.count_documents({**query_filter, "feedback_type": "dislike"})
        total_feedback = positive_feedback + negative_feedback
        
        feedback_rate = (total_feedback / total_chats * 100) if total_chats > 0 else 0
        
        return DashboardMetrics(
            total_chats=total_chats,
            resolved_chats=resolved_chats,
            unresolved_chats=unresolved_chats,
            resolution_rate=(resolved_chats / total_chats * 100) if total_chats > 0 else 0,
            avg_response_time=avg_response_time,
            positive_feedback=positive_feedback,
            negative_feedback=negative_feedback,
            feedback_rate=feedback_rate
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/analytics")
async def get_chat_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None)
):
    """Get detailed chat analytics"""
    try:
        # Build query filter
        query_filter = {}
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                date_filter["$lte"] = datetime.fromisoformat(end_date + "T23:59:59")
            query_filter["timestamp"] = date_filter
        
        if user_id:
            query_filter["user_id"] = user_id
        
        # Get chats by category
        category_pipeline = [
            {"$match": query_filter},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        category_results = list(chat_logs.aggregate(category_pipeline))
        categories = {result["_id"]: result["count"] for result in category_results}
        
        # Get chats by language
        language_pipeline = [
            {"$match": query_filter},
            {"$group": {"_id": "$language", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        language_results = list(chat_logs.aggregate(language_pipeline))
        languages = {result["_id"]: result["count"] for result in language_results}
        
        # Get daily chat counts for the last 30 days
        end_date_obj = datetime.now() if not end_date else datetime.fromisoformat(end_date)
        start_date_obj = end_date_obj - timedelta(days=30) if not start_date else datetime.fromisoformat(start_date)
        
        daily_pipeline = [
            {"$match": {
                **query_filter,
                "timestamp": {"$gte": start_date_obj, "$lte": end_date_obj}
            }},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        daily_results = list(chat_logs.aggregate(daily_pipeline))
        daily_chats = {result["_id"]: result["count"] for result in daily_results}
        
        # Get confidence score distribution
        confidence_pipeline = [
            {"$match": query_filter},
            {"$bucket": {
                "groupBy": "$confidence",
                "boundaries": [0, 0.2, 0.4, 0.6, 0.8, 1.0],
                "default": "other",
                "output": {"count": {"$sum": 1}}
            }}
        ]
        
        confidence_results = list(chat_logs.aggregate(confidence_pipeline))
        confidence_distribution = {}
        for result in confidence_results:
            if result["_id"] != "other":
                range_str = f"{result['_id']}-{result['_id'] + 0.2:.1f}"
                confidence_distribution[range_str] = result["count"]
        
        return {
            "categories": categories,
            "languages": languages,
            "daily_chats": daily_chats,
            "confidence_distribution": confidence_distribution
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/sentiment")
async def get_sentiment_analysis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None)
):
    """Get sentiment analysis of chats"""
    try:
        # Build query filter
        query_filter = {}
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                date_filter["$lte"] = datetime.fromisoformat(end_date + "T23:59:59")
            query_filter["timestamp"] = date_filter
        
        if user_id:
            query_filter["user_id"] = user_id
        
        # Get recent chats for sentiment analysis
        chats = list(chat_logs.find(query_filter).limit(1000))
        
        sentiment_counts = defaultdict(int)
        
        if sentiment_analyzer and chats:
            for chat in chats:
                try:
                    # Analyze message sentiment
                    message_text = chat.get("message", "")
                    if message_text:
                        result = sentiment_analyzer(message_text)[0]
                        sentiment_label = result["label"].lower()
                        
                        # Map sentiment labels
                        if "positive" in sentiment_label or sentiment_label == "label_2":
                            sentiment_counts["positive"] += 1
                        elif "negative" in sentiment_label or sentiment_label == "label_0":
                            sentiment_counts["negative"] += 1
                        else:
                            sentiment_counts["neutral"] += 1
                    else:
                        sentiment_counts["neutral"] += 1
                        
                except Exception as e:
                    print(f"Error analyzing sentiment for chat: {e}")
                    sentiment_counts["neutral"] += 1
        else:
            # Fallback: use feedback as sentiment indicator
            for chat in chats:
                feedback_type = chat.get("feedback_type")
                if feedback_type == "like":
                    sentiment_counts["positive"] += 1
                elif feedback_type == "dislike":
                    sentiment_counts["negative"] += 1
                else:
                    sentiment_counts["neutral"] += 1
        
        total_analyzed = sum(sentiment_counts.values())
        sentiment_percentages = {}
        
        if total_analyzed > 0:
            for sentiment, count in sentiment_counts.items():
                sentiment_percentages[sentiment] = round((count / total_analyzed) * 100, 2)
        
        return {
            "sentiment_counts": dict(sentiment_counts),
            "sentiment_percentages": sentiment_percentages,
            "total_analyzed": total_analyzed
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sentiment analysis: {str(e)}")

@router.get("/support-queue")
async def get_support_queue(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Limit results")
):
    """Get unresolved queries in support queue"""
    try:
        query_filter = {}
        if status:
            query_filter["status"] = status
        
        queue_items = list(
            support_queue.find(query_filter)
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string for JSON serialization
        for item in queue_items:
            item["_id"] = str(item["_id"])
            
        return {
            "queue_items": queue_items,
            "total_count": support_queue.count_documents(query_filter)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get support queue: {str(e)}")

@router.get("/recent-chats")
async def get_recent_chats(
    limit: int = Query(20, description="Limit results"),
    user_id: Optional[str] = Query(None)
):
    """Get recent chat conversations"""
    try:
        query_filter = {}
        if user_id:
            query_filter["user_id"] = user_id
        
        recent_chats = list(
            chat_logs.find(query_filter)
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string and format timestamps
        for chat in recent_chats:
            chat["_id"] = str(chat["_id"])
            if isinstance(chat.get("timestamp"), datetime):
                chat["timestamp"] = chat["timestamp"].isoformat()
            if isinstance(chat.get("feedback_timestamp"), datetime):
                chat["feedback_timestamp"] = chat["feedback_timestamp"].isoformat()
        
        return {"recent_chats": recent_chats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent chats: {str(e)}")
