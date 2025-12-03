from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import json
from datetime import datetime

from .models import ChatRequest, ChatResponse, FeedbackRequest
from langgraph_agents.agent import ChatbotAgent
from utils.language_detector import LanguageDetector
router = APIRouter()

# Initialize components
chatbot_agent = ChatbotAgent()
language_detector = LanguageDetector()

# Simple in-memory storage for chat logs
chat_logs_storage = []
support_queue_storage = []

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint that processes user messages"""
    try:
        # Detect language
        detected_language = language_detector.detect_language(request.message)
        
        # Use specified language if provided, otherwise use detected
        language = request.language or detected_language
        
        # Process chat with agent
        response = await chatbot_agent.process_chat(
            message=request.message,
            language=language,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # Store chat log
        chat_log = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "message": request.message,
            "response": response["response"],
            "language": language,
            "category": response["category"],
            "confidence": response["confidence"],
            "timestamp": datetime.utcnow().isoformat(),
            "resolved": response["confidence"] > 0.5
        }
        
        chat_logs_storage.append(chat_log)
        
        # Add to support queue if unresolved
        if not chat_log["resolved"]:
            support_queue_storage.append({
                "chat_id": f"{request.session_id}_{len(chat_logs_storage)}",
                "user_id": request.user_id,
                "session_id": request.session_id,
                "message": request.message,
                "response": response["response"],
                "category": response["category"],
                "confidence": response["confidence"],
                "timestamp": datetime.utcnow().isoformat(),
                "status": "pending"
            })
        
        return ChatResponse(
            response=response["response"],
            confidence=response["confidence"],
            category=response["category"],
            language=language,
            resolved=chat_log["resolved"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback for a chat response"""
    try:
        # Find and update the chat log with feedback
        for chat_log in reversed(chat_logs_storage):
            if chat_log["session_id"] == feedback.session_id:
                chat_log["feedback_type"] = feedback.feedback_type
                chat_log["feedback_comment"] = feedback.comment
                chat_log["feedback_timestamp"] = datetime.utcnow().isoformat()
                
                # If negative feedback, add to support queue
                if feedback.feedback_type == "dislike":
                    support_queue_storage.append({
                        "chat_id": f"{feedback.session_id}_{len(support_queue_storage)}",
                        "user_id": chat_log["user_id"],
                        "session_id": feedback.session_id,
                        "message": chat_log["message"],
                        "response": chat_log["response"],
                        "category": chat_log["category"],
                        "confidence": chat_log["confidence"],
                        "feedback_comment": feedback.comment,
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "pending"
                    })
                return {"status": "success", "message": "Feedback submitted successfully"}
        
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chatbot"}

@router.post("/reindex-documents")
async def reindex_documents(background_tasks: BackgroundTasks):
    """Manually trigger document reindexing"""
    try:
        from utils.document_processor import DocumentProcessor
        from vector_store.chroma_store import ChromaStore
        
        background_tasks.add_task(reindex_documents_task)
        return {"status": "success", "message": "Document reindexing started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")

async def reindex_documents_task():
    """Background task for document reindexing"""
    try:
        vector_store = ChromaStore()
        doc_processor = DocumentProcessor()
        
        # Clear existing documents
        vector_store.clear_collection()
        
        # Reprocess all documents
        input_folder = "input"
        if os.path.exists(input_folder):
            await doc_processor.process_folder(input_folder, vector_store)
            print("Document reindexing completed successfully")
        
    except Exception as e:
        print(f"Document reindexing failed: {e}")
