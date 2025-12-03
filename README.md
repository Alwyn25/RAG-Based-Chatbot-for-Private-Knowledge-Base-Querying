# Customer Support Chatbot System

## Overview

This is a modular, microservice-based customer support chatbot system using Agentic RAG (Retrieval-Augmented Generation) architecture. The system provides multilingual support (English and Arabic), intelligent document processing, and real-time analytics through a comprehensive dashboard.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The system follows a microservices architecture with three main components:

1. **Chatbot Service** (Port 8000): Core AI-powered chat functionality using FastAPI
2. **Dashboard Service** (Port 5000): Analytics and monitoring interface using FastAPI + Jinja2
3. **Chat Widget**: Frontend integration component for websites

### Key Architectural Decisions

**Microservices Approach**: Chosen to ensure modularity, scalability, and independent deployment of services. This allows for easier maintenance and the ability to scale individual components based on demand.

**Agentic RAG with LangGraph**: Implements an agent-based approach for more sophisticated conversation handling, allowing the system to make decisions about document retrieval, response generation, and escalation strategies.

**Vector Database Integration**: Uses ChromaDB for efficient similarity search and document retrieval, enabling contextual responses based on indexed documentation.

## Key Components

### 1. AI Agent Framework
- **Technology**: LangGraph + Gemini API
- **Purpose**: Handles conversation flow, category classification, and response generation
- **Features**: 
  - Query categorization (Product FAQ, Tech issue, Transactional)
  - Confidence scoring
  - Language detection and processing

### 2. Document Processing Pipeline
- **Supported Formats**: PDF, DOCX, CSV, Markdown, HTML, TXT
- **Embedding Model**: Multilingual sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **Storage**: ChromaDB for vector embeddings, MongoDB for metadata

### 3. Language Support
- **Languages**: English and Arabic with auto-detection
- **Detection**: Uses langdetect library with fallback mechanisms
- **Embeddings**: Multilingual model ensures cross-language semantic understanding

### 4. Chat Widget
- **Integration**: Embeddable JavaScript widget for websites
- **Features**: Responsive design, real-time messaging, feedback collection
- **Customization**: CSS-based styling for brand integration

### 5. Analytics Dashboard
- **Technology**: FastAPI backend with Bootstrap frontend
- **Metrics**: Resolution rates, response times, sentiment analysis, category distribution
- **Visualization**: Chart.js for interactive data visualization

## Data Flow

1. **Document Ingestion**: Documents placed in `input/` folder are automatically processed on startup
2. **Embedding Generation**: Text chunks are converted to vector embeddings using multilingual models
3. **Vector Storage**: Embeddings stored in ChromaDB with metadata in MongoDB
4. **Chat Processing**: 
   - User message → Language detection → Category classification
   - Vector similarity search → Context retrieval → LLM response generation
   - Response logging and feedback collection
5. **Analytics Pipeline**: Chat logs processed for dashboard metrics and insights

## External Dependencies

### APIs and Services
- **Gemini API**: Primary LLM for response generation (requires GEMINI_API_KEY)
- **MongoDB**: Document metadata, chat logs, and analytics storage
- **ChromaDB**: Vector embeddings and similarity search

### Python Libraries
- **Core**: FastAPI, uvicorn, pydantic
- **AI/ML**: sentence-transformers, langdetect, transformers (optional for sentiment)
- **Document Processing**: PyPDF2, python-docx, pandas, beautifulsoup4, markdown
- **Database**: pymongo, chromadb

### Frontend Dependencies
- **Bootstrap 5.1.3**: UI framework for dashboard
- **Chart.js**: Data visualization
- **Font Awesome**: Icons and visual elements

## Deployment Strategy

### Development Environment
- **Chatbot Service**: `uvicorn main:app --reload --port 8000`
- **Dashboard Service**: `uvicorn main:app --reload --port 5000`
- **MongoDB**: Local instance or MongoDB Atlas
- **Document Storage**: Local `input/` folder with automatic processing

### Production Considerations
- **Containerization**: Services designed for Docker deployment
- **Environment Variables**: Configuration through `.env` files
- **Scalability**: Microservices can be deployed independently
- **Monitoring**: Health check endpoints available for load balancers

### Configuration Requirements
- `MONGODB_URL`: MongoDB connection string
- `GEMINI_API_KEY`: Google Gemini API authentication
- Input folder structure for document processing
- CORS configuration for cross-origin requests

The system is designed for easy deployment with minimal configuration, supporting both development and production environments through environment-based configuration management.