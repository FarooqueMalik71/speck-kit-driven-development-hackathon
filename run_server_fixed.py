import sys
import os

# Add the backend/src directory to the Python path so imports work correctly
backend_src_dir = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src_dir)

# Now import and run the main application
from main import app
import uvicorn

if __name__ == "__main__":
    print("Starting server on http://0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)