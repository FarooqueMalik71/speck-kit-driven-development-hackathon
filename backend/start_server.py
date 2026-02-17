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
        # Import the app after setting up basic logging
        import uvicorn
        from src.main import app

        print("[SUCCESS] Server imported successfully!")
        print("[SUCCESS] Services available:", os.environ.get('SERVICES_AVAILABLE', 'Not checked yet'))

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
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    start_server()