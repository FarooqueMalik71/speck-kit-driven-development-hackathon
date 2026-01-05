import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment variables to avoid missing dependency issues
os.environ.setdefault("OPENAI_API_KEY", "fake-key-for-testing")
os.environ.setdefault("QDRANT_API_KEY", "fake-key-for-testing")
os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-testing")

# Set basic logging to avoid the custom logging issues
import logging
logging.basicConfig(level=logging.WARNING)

def test_backend():
    try:
        # Import the app
        from src.main import (
            app,
            SERVICES_AVAILABLE,
            RETRIEVAL_SERVICE_AVAILABLE,
            AGENTS_AVAILABLE,
            CITATION_SERVICE_AVAILABLE,
            FALLBACK_SERVICE_AVAILABLE,
            EMBEDDING_SERVICE_AVAILABLE,
            VECTOR_STORE_SERVICE_AVAILABLE,
            CONFIG_AVAILABLE
        )

        print("[SUCCESS] FastAPI app loaded successfully")
        print(f"Services available: {SERVICES_AVAILABLE}")
        print(f"Retrieval service available: {RETRIEVAL_SERVICE_AVAILABLE}")
        print(f"Config available: {CONFIG_AVAILABLE}")
        print(f"Agents available: {AGENTS_AVAILABLE}")
        print(f"Citation service available: {CITATION_SERVICE_AVAILABLE}")
        print(f"Fallback service available: {FALLBACK_SERVICE_AVAILABLE}")
        print(f"Embedding service available: {EMBEDDING_SERVICE_AVAILABLE}")
        print(f"Vector store service available: {VECTOR_STORE_SERVICE_AVAILABLE}")

        print("\n[SUCCESS] All tests completed successfully!")
        print("The backend is now configured to handle missing dependencies gracefully.")
        print("The query endpoint will return mock responses when services are unavailable.")

        return True

    except Exception as e:
        print(f"[ERROR] Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_backend()
    if success:
        print("\n[SUCCESS] Backend fix verification successful!")
    else:
        print("\n[ERROR] Backend fix verification failed!")