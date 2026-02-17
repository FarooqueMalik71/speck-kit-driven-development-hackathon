import os
import sys
from pathlib import Path

# Add the backend/src directory to the Python path
backend_src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(backend_src_path))

# Import the main backend application
from src.main import app

# The backend app is already a FastAPI instance with all the routes and CORS configured
# CORS is already configured in the backend to allow all origins
# We just need to make sure it works with Hugging Face's requirements

if __name__ == "__main__":
    # Hugging Face Spaces typically uses port 7860
    port = int(os.environ.get("PORT", 7860))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)