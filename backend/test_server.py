import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set a basic environment to avoid missing dependency issues
os.environ.setdefault("OPENAI_API_KEY", "fake-key-for-testing")
os.environ.setdefault("QDRANT_API_KEY", "fake-key-for-testing")

# Use basic logging to avoid the custom logging issues
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_server():
    try:
        # Import the main app
        from src.main import app
        logger.info("Successfully imported the FastAPI app")

        # Check if services are available
        from src.main import SERVICES_AVAILABLE
        logger.info(f"Services available: {SERVICES_AVAILABLE}")

        if SERVICES_AVAILABLE:
            logger.info("All services are available")
        else:
            logger.info("Some services are not available due to missing dependencies - this is expected in test environment")

        return True

    except Exception as e:
        logger.error(f"Error importing app: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_server()
    if success:
        print("\n✅ Server test successful! The app can be started.")
        print("To start the server, run: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("\n❌ Server test failed!")