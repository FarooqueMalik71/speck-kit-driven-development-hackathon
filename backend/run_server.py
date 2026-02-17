#!/usr/bin/env python3
"""
Simple script to run the FastAPI server for the AI Chatbot Backend
"""

import sys
import os

# Add the src directory to the Python path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_dir)

from src.main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting AI Chatbot Backend Server...")
    print("📍 API docs will be available at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("🤖 Query endpoint at: http://localhost:8000/query")
    print("Press Ctrl+C to stop the server")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )