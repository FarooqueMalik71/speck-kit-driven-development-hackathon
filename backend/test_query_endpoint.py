import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment variables to avoid missing dependency issues
os.environ.setdefault("OPENAI_API_KEY", "fake-key-for-testing")
os.environ.setdefault("QDRANT_API_KEY", "fake-key-for-testing")
os.environ.setdefault("NEON_DATABASE_URL", "fake-url-for-testing")
os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-testing")

# Set basic logging to avoid the custom logging issues
import logging
logging.basicConfig(level=logging.WARNING)

# Now import and run the app
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    import asyncio
    import threading
    import time
    import requests

    # Import the app
    from src.main import app

    print("✅ FastAPI app loaded successfully")
    print("✅ Services available:", "src.main" in sys.modules)

    # Start the server in a background thread
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(2)

    # Test the root endpoint
    try:
        response = requests.get("http://127.0.0.1:8001/")
        print(f"Root endpoint status: {response.status_code}")
        print(f"Root endpoint response: {response.json() if response.status_code == 200 else 'Error'}")
    except Exception as e:
        print(f"Error testing root endpoint: {str(e)}")

    # Test the health endpoint
    try:
        response = requests.get("http://127.0.0.1:8001/health")
        print(f"Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
    except Exception as e:
        print(f"Error testing health endpoint: {str(e)}")

    # Test the query endpoint
    print("\n--- Testing Query Endpoint ---")
    
    # Test multiple queries
    test_queries = [
        "What is robotics?",
        "What is physical AI?",
        "Tell me about humanoid robots"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        query_data = {
            "query": query,
            "context_ids": [],
            "mode": "full_book"
        }

        try:
            response = requests.post("http://127.0.0.1:8001/query", json=query_data)
            print(f"Query endpoint status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("Query response successful!")
                print(f"Answer: {result.get('answer', 'N/A')[:150]}...")
                print(f"Confidence: {result.get('confidence', 'N/A')}")
                print(f"Citations: {result.get('citations', 'N/A')}")
            else:
                print(f"Query endpoint failed: {response.text}")
        except Exception as e:
            print(f"Error testing query endpoint: {str(e)}")

    print("\nAll endpoints tested!")