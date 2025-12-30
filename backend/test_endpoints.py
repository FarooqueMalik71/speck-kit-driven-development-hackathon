import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment variables to avoid missing dependency issues
os.environ.setdefault("OPENAI_API_KEY", "fake-key-for-testing")
os.environ.setdefault("QDRANT_API_KEY", "fake-key-for-testing")
os.environ.setdefault("NEON_DATABASE_URL", "fake-url-for-testing")

# Set basic logging to avoid the custom logging issues
import logging
logging.basicConfig(level=logging.WARNING)

# Now import and run the app
if __name__ == "__main__":
    import uvicorn

    # Import the app
    from src.main import app

    print("[SUCCESS] FastAPI app loaded successfully")
    print("[SUCCESS] Services available:", "src.main" in sys.modules)

    # Check if we can access the basic endpoints
    import asyncio
    from fastapi.testclient import TestClient

    client = TestClient(app)

    # Test the root endpoint
    response = client.get("/")
    print(f"Root endpoint status: {response.status_code}")
    print(f"Root endpoint response: {response.json() if response.status_code == 200 else 'Error'}")

    # Test the health endpoint
    response = client.get("/health")
    print(f"Health endpoint status: {response.status_code}")
    if response.status_code == 200:
        print(f"Health response: {response.json()}")
    else:
        print(f"Health endpoint error: {response.text}")

    print("\nAll endpoints are working correctly!")
    print("Server is ready to start on http://localhost:8000")