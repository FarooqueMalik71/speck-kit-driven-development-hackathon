# Local Testing Guide: Frontend-Backend Integration

This guide will help you test the frontend-backend integration locally before deploying to production.

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- Git

## Step 1: Start the Backend Server

### Option A: Using the Test Backend (Recommended for local testing)

If the main backend has dependency issues, use the test backend:

1. Open a terminal/command prompt
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```

3. Create and activate a virtual environment:
   ```bash
   # On Windows:
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install minimal dependencies for the test backend:
   ```bash
   pip install fastapi uvicorn
   ```

5. Start the test backend server:
   ```bash
   python test_backend.py
   ```

   The server should start on `http://localhost:8000`

### Option B: Using the Main Backend

If you want to try the main backend:

1. Open a terminal/command prompt
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```

3. Create and activate a virtual environment:
   ```bash
   # On Windows:
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install backend dependencies:
   ```bash
   pip install -r requirements_basic.txt
   # OR if you want all dependencies:
   pip install -r requirements.txt
   ```

5. Create a .env file in the backend directory with minimal configuration:
   ```bash
   # backend/.env
   GEMINI_API_KEY=your-gemini-api-key-here  # Get from https://aistudio.google.com/
   QDRANT_HOST=localhost
   LLM_PROVIDER=gemini
   MODEL_NAME=gemini-1.5-flash
   ```

6. Start the main backend server:
   ```bash
   python start_server.py
   ```

   The server should start on `http://localhost:8000`

7. Test the backend is working:
   - Open browser to `http://localhost:8000` - should show welcome message
   - Test health endpoint: `http://localhost:8000/health`
   - The server should show `[SUCCESS] Server imported successfully!`

## Step 2: Start the Frontend Server

1. Open a **new** terminal/command prompt (keep the backend running)
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Install frontend dependencies:
   ```bash
   npm install
   ```

4. Create a .env file in the frontend directory:
   ```bash
   # frontend/.env
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```

5. Start the frontend development server:
   ```bash
   npm start
   ```

   The frontend should start on `http://localhost:3000`

## Step 3: Test the Integration

1. With both servers running:
   - Backend: `http://localhost:8000`
   - Frontend: `http://localhost:3000`

2. Open your browser to `http://localhost:3000/ai-chat`

3. Test the AI chat functionality:
   - Type a question in the chat interface
   - The frontend should make a POST request to `http://localhost:8000/query`
   - You should receive a response from the backend

4. Check the browser's developer tools:
   - Open DevTools (F12)
   - Go to the "Network" tab
   - Send a message and verify the request to `/query` is made
   - Check the "Console" tab for any error messages

## Step 4: Test Backend API Directly

You can also test the backend API directly using curl or a tool like Postman:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Physical AI?",
    "context_ids": [],
    "mode": "full_book"
  }'
```

## Troubleshooting Common Issues

### Issue: Backend not starting
- **Error**: Import errors or missing dependencies
- **Solution**: Use the test backend (`python test_backend.py`) for local testing, or install all dependencies with `pip install -r requirements.txt`

### Issue: Main backend shows "AI services are not available due to missing dependencies"
- **Error**: 503 error from the main backend
- **Solution**: This is a common issue with the main backend. Use the test backend for local development: `python test_backend.py`

### Issue: Frontend can't connect to backend
- **Error**: CORS errors or network errors
- **Solution**: Check that backend is running on http://localhost:8000 and that the frontend .env has the correct URL

### Issue: Backend returns 500 error
- **Error**: Internal server error
- **Solution**: Check that required environment variables (like API keys) are set

### Issue: Frontend shows "API request failed"
- **Error**: Network error in the frontend
- **Solution**: Verify the backend is running and accessible, check browser console for specific error messages

### Issue: Services not available error
- **Error**: The main backend shows "AI services are not available due to missing dependencies"
- **Solution**: This occurs when service imports fail. Use the test backend for local development, which bypasses these dependencies.

## Expected Behavior

When properly integrated:
1. Frontend should connect to backend at http://localhost:8000
2. AI chat should return responses from the backend
3. No CORS or network errors should appear in browser console
4. Backend logs should show incoming requests

## Next Steps

Once local testing is successful:
1. Deploy the backend to Hugging Face Spaces
2. Update the frontend .env to use the Hugging Face backend URL
3. Deploy the frontend to Vercel
4. Test the production integration

## Environment Variables Reference

### Backend (.env in backend directory)
```
GEMINI_API_KEY=your-gemini-api-key  # Required
QDRANT_HOST=localhost               # For local testing
LLM_PROVIDER=gemini                 # Default provider
MODEL_NAME=gemini-1.5-flash         # Model to use
```

### Frontend (.env in frontend directory)
```
REACT_APP_BACKEND_URL=http://localhost:8000  # Local development
# For production: REACT_APP_BACKEND_URL=https://your-space-name.hf.space
```