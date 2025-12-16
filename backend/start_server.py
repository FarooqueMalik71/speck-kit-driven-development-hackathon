import os
import sys
import logging
from pathlib import Path

# Set up basic logging first to avoid the custom logging issue
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def start_server():
    """Start the FastAPI server with minimal dependencies"""
    try:
        # Set environment variables to avoid missing dependency issues
        os.environ.setdefault("OPENAI_API_KEY", "fake-key-for-testing")
        os.environ.setdefault("QDRANT_API_KEY", "fake-key-for-testing")
        os.environ.setdefault("NEON_DATABASE_URL", "fake-url-for-testing")

        # Import the app after setting up basic logging
        import uvicorn
        from src.main import app

        print("✅ Server imported successfully!")
        print("✅ Services available:", os.environ.get('SERVICES_AVAILABLE', 'Not checked yet'))

        print("\nStarting server on http://0.0.0.0:8000")
        print("Press Ctrl+C to stop the server")

        # Start the server
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Set to False to avoid issues during testing
            log_level="info"
        )

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    start_server()