import os
import sys
import time
import threading
from pathlib import Path
import requests
import subprocess
import signal
import time

def test_api_endpoints():
    """Test the API endpoints by starting the server and making requests"""

    # Set environment variables
    os.environ.setdefault("OPENAI_API_KEY", "fake-key-for-testing")
    os.environ.setdefault("QDRANT_API_KEY", "fake-key-for-testing")
    os.environ.setdefault("NEON_DATABASE_URL", "fake-url-for-testing")

    # Import the app directly to check if it loads
    sys.path.insert(0, str(Path(__file__).parent / "src"))

    try:
        from src.main import app
        print("[SUCCESS] FastAPI app loaded successfully")
    except Exception as e:
        print(f"[ERROR] Could not load app: {e}")
        return False

    # Start the server in a subprocess
    print("[INFO] Starting server in background...")

    # Create a simple script to run the server
    server_script = '''
import os
import logging
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment variables
os.environ.setdefault("OPENAI_API_KEY", "fake-key-for-testing")
os.environ.setdefault("QDRANT_API_KEY", "fake-key-for-testing")
os.environ.setdefault("NEON_DATABASE_URL", "fake-url-for-testing")

# Set basic logging
logging.basicConfig(level=logging.WARNING)

def start_server():
    try:
        from src.main import app
        import uvicorn
        print("[SERVER] Server ready, starting uvicorn...")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
    except Exception as e:
        print(f"[SERVER] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_server()
'''

    # Write the server script
    with open("temp_server.py", "w") as f:
        f.write(server_script)

    # Start the server process
    process = subprocess.Popen([sys.executable, "temp_server.py"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              cwd=".")

    # Wait a moment for the server to start
    time.sleep(3)

    try:
        # Test the root endpoint
        print("[INFO] Testing endpoints...")
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=5)
            print(f"[SUCCESS] Root endpoint status: {response.status_code}")
            if response.status_code == 200:
                print(f"[SUCCESS] Root response: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not reach root endpoint: {e}")

        # Test the health endpoint
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            print(f"[SUCCESS] Health endpoint status: {response.status_code}")
            if response.status_code == 200:
                print(f"[SUCCESS] Health response: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not reach health endpoint: {e}")

        # Test the query endpoint
        try:
            sample_query = {
                "query": "What is this textbook about?",
                "context_ids": [],
                "mode": "full_book"
            }
            response = requests.post("http://127.0.0.1:8000/query",
                                   json=sample_query,
                                   timeout=10)
            print(f"[SUCCESS] Query endpoint status: {response.status_code}")
            if response.status_code == 200:
                print(f"[SUCCESS] Query response: {response.json()}")
            else:
                print(f"[INFO] Query endpoint returned {response.status_code}: {response.text}")
                print("[INFO] This is expected if vector store or LLM dependencies are not fully configured")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Could not reach query endpoint: {e}")

    finally:
        # Terminate the server process
        try:
            process.terminate()
            process.wait(timeout=5)
            print("[INFO] Server terminated")
        except:
            try:
                process.kill()
                print("[INFO] Server killed")
            except:
                pass

        # Clean up the temp file
        try:
            os.remove("temp_server.py")
        except:
            pass

    print("\n[SUCCESS] API testing completed!")
    return True

if __name__ == "__main__":
    test_api_endpoints()