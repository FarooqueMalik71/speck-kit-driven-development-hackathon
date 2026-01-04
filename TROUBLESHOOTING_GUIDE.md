# Troubleshooting Guide: Hugging Face Backend Deployment

## Issue: 503 Service Unavailable Error

The frontend is receiving a 503 error when trying to connect to the backend API at `https://farooquemalik50871-AI-Book-Backend.hf.space/query`. This indicates that the Hugging Face Space backend is not running properly.

## Root Causes and Solutions

### 1. Missing API Keys in Hugging Face Space Secrets

**Problem**: The backend requires API keys to function properly, but they may not be configured in your Hugging Face Space.

**Solution**:
1. Go to your Hugging Face Space
2. Navigate to the "Settings" tab
3. Go to "Secrets" section
4. Add the following secrets:
   - `GEMINI_API_KEY`: Your Google Gemini API key (required)
   - `QDRANT_API_KEY`: Your Qdrant vector database API key (if using cloud)
   - `OPENAI_API_KEY`: Your OpenAI API key (optional, for fallback)
   - `OPENROUTER_API_KEY`: Your OpenRouter API key (optional, for fallback)
   - `LLM_PROVIDER`: Set to "gemini" (or your preferred provider)

### 2. Backend Service Not Starting Properly

**Problem**: The backend may be failing to start due to missing dependencies or configuration issues.

**Solution**:
1. Check the Hugging Face Space logs:
   - Go to your Space page
   - Click on the "Logs" tab
   - Look for error messages during startup
2. Common issues to look for:
   - Missing dependencies
   - Import errors
   - Configuration validation failures

### 3. Using the Correct Dockerfile

**Problem**: The Space might not be using the correct Dockerfile for deployment.

**Solution**:
1. Make sure your Hugging Face Space is configured to use `Dockerfile.hf`
2. In your Space settings, ensure the "Dockerfile" path is set correctly
3. If using the Docker SDK option, verify the Dockerfile name matches

### 4. Requirements Issues

**Problem**: The dependencies in requirements.txt may be too heavy or have conflicts for Hugging Face.

**Solution**:
1. The repository now includes `backend/requirements_hf.txt` which is optimized for Hugging Face deployment
2. Use the `Dockerfile.hf` which uses this lighter requirements file
3. If the Space still fails, try creating an even more minimal requirements file

## Steps to Fix the Current Issue

### Step 1: Check Space Status
1. Go to: https://huggingface.co/spaces/farooquemalik50871/AI-Book-Backend
2. Check if the Space is running (green "Running" indicator)
3. If it's not running, click "Restart Space"

### Step 2: Verify Secrets Configuration
1. In your Space settings, check that all required API keys are properly set as secrets
2. Make sure the secret names match exactly what the backend expects

### Step 3: Check Build Logs
1. In your Space, go to the "Logs" tab
2. Look for any build-time errors
3. Look for runtime errors after the build completes

### Step 4: Verify Dockerfile Usage
Make sure your Hugging Face Space is using the correct Dockerfile:
- If using Docker SDK: Ensure it's using `Dockerfile.hf`
- The Dockerfile should install dependencies and start the app correctly

### Step 5: Test API Endpoints
Once the Space is running, test these endpoints:
- `GET /` - Should return a welcome message
- `GET /health` - Should return health status
- `POST /query` - Should accept queries (with proper request body)

## Alternative: Use Requirements_Basic.txt

If the deployment is still failing due to heavy dependencies, you can use the minimal requirements:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
qdrant-client==1.8.0
openai==1.3.5
langchain==0.0.339
langchain-openai==0.0.5
python-dotenv==1.0.0
numpy==1.24.3
```

## Quick Fix Checklist

- [ ] API keys properly configured in Space secrets
- [ ] Space is running (not sleeping)
- [ ] Using the correct Dockerfile (`Dockerfile.hf`)
- [ ] Requirements file has all necessary dependencies
- [ ] Backend logs show no startup errors
- [ ] Health endpoint (`/`) returns successfully
- [ ] Query endpoint (`/query`) is available

## Restarting Your Space

If changes were made to the repository:
1. Push updates to GitHub
2. Go to your Hugging Face Space
3. In the "Files" tab, click the refresh icon or restart the Space
4. Monitor the logs during rebuild

## Testing the Fix

After implementing the fixes:
1. Wait for the Space to fully restart
2. Test the endpoint directly in your browser: `https://[your-username]-[space-name].hf.space/`
3. Then test from the frontend: `https://speck-kit-driven-development-hackat-nine.vercel.app/ai-chat`