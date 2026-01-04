"""
Minimal test backend for local development
This creates a simple API that returns mock responses for testing
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

# Enable CORS for local development
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Test AI Textbook Platform API",
    description="Minimal test backend for local development",
    version="1.0.0"
)

# Add CORS middleware to allow all origins for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/response models
class QueryRequest(BaseModel):
    query: str
    context_ids: List[str] = []
    mode: str = "full_book"  # "full_book" or "selected_text"

class QueryResponse(BaseModel):
    answer: str
    citations: List[str] = []
    confidence: float = 0.0
    is_confident: bool = False
    sources: List[str] = []
    boundary_compliance: float = 0.0
    needs_fact_check: bool = False

@app.get("/")
def read_root():
    return {"message": "Test AI Textbook Platform API - Ready for local testing"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "test-textbook-api",
        "environment": "development",
        "log_level": "INFO"
    }

@app.post("/query", response_model=QueryResponse)
def query_textbook(request: QueryRequest):
    """Test endpoint that returns mock responses for local development"""
    try:
        # Generate a mock response based on the query
        answer = f"This is a test response for your query: '{request.query}'. This is a simulated answer from the AI assistant for local testing purposes. In the full implementation, this would connect to the RAG system to provide contextually relevant answers from the textbook content."

        # Generate some mock citations
        citations = [
            "Introduction to Physical AI & Humanoid Robotics",
            "Overview of Physical AI and Humanoid Robotics",
            "Chapter 2: Fundamentals of AI"
        ]

        # Generate mock sources
        sources = [
            "docs/intro.md",
            "docs/overview.md",
            "docs/fundamentals.md"
        ]

        return QueryResponse(
            answer=answer,
            citations=citations,
            confidence=0.85,
            is_confident=True,
            sources=sources,
            boundary_compliance=1.0,
            needs_fact_check=False
        )
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting test server on http://localhost:{port}")
    print("This is a minimal test backend for local development")
    print("The /query endpoint returns mock responses for testing")
    uvicorn.run(app, host="0.0.0.0", port=port)