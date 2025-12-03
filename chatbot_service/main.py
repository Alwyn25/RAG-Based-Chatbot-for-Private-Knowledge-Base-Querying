import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.api import router
from utils.document_processor import DocumentProcessor
from vector_store.chroma_store import ChromaStore

app = FastAPI(title="Customer Support Chatbot", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Initialize document processing and vector store on startup"""
    print("Initializing chatbot service...")
    
    # Initialize vector store
    vector_store = ChromaStore()
    
    # Process documents from input folder
    doc_processor = DocumentProcessor()
    input_folder = "input"
    
    if os.path.exists(input_folder):
        await doc_processor.process_folder(input_folder, vector_store)
        print(f"Processed documents from {input_folder}")
    else:
        print(f"Input folder {input_folder} not found. Creating it...")
        os.makedirs(input_folder, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Customer Support Chatbot Service", "status": "running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
