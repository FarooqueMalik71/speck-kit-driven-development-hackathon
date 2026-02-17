from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from pydantic import BaseModel
import os
import asyncio
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Settings:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "fake-key-for-testing")

settings = Settings()

app = FastAPI(
    title="AI-Native Textbook Platform API",
    description="API for the Physical AI & Humanoid Robotics textbook platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/response models
class QueryRequest(BaseModel):
    query: str
    context_ids: list = []
    mode: str = "full_book"  # "full_book" or "selected_text"

class QueryResponse(BaseModel):
    answer: str
    citations: list = []
    confidence: float = 0.0
    is_confident: bool = False
    sources: list = []
    boundary_compliance: float = 0.0
    needs_fact_check: bool = False

@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Welcome to the AI-Native Textbook Platform API"}

@app.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "textbook-api",
        "environment": "production",
        "log_level": "INFO"
    }

@app.post("/query", response_model=QueryResponse)
def query_textbook(request: QueryRequest):
    """Query the textbook with AI-powered responses"""
    try:
        # For this minimal version, we'll return a mock response
        # In a full implementation, this would connect to actual AI services
        answer = f"Based on the textbook content, here's information about: {request.query}. [Note: This is a simulated response from the minimal backend.]"

        # Mock response with reasonable defaults
        return QueryResponse(
            answer=answer,
            citations=["Mock Citation - Textbook Chapter 1", "Mock Citation - Introduction Section"],
            confidence=0.7,
            is_confident=True,
            sources=["mock_source.pdf"],
            boundary_compliance=0.8,
            needs_fact_check=False
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Additional endpoint for testing
@app.get("/test")
def test_endpoint():
    return {"status": "ok", "message": "Backend is running correctly"}

if __name__ == "__main__":
    import uvicorn
    print("Starting server on 0.0.0.0:8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )