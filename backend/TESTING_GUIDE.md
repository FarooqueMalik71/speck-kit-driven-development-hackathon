# Backend Testing Guide

## 🚀 How to Test Your AI Chatbot Backend

### Method 1: Automated Testing (Recommended)

Run the comprehensive test script that checks all endpoints:

```bash
cd backend
python test_endpoints.py
```

This will:
- ✅ Load the FastAPI app
- ✅ Test the root endpoint (`/`)
- ✅ Test the health endpoint (`/health`)
- ✅ Test the query endpoint (`/query`) with sample data
- ✅ Show response status and content

### Method 2: Manual Server Testing

1. **Start the server:**
```bash
cd backend
python run_server.py
```

2. **Test endpoints manually using curl:**

```bash
# Test root endpoint
curl http://localhost:8000/

# Test health endpoint
curl http://localhost:8000/health

# Test query endpoint
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is robotics?",
       "context_ids": [],
       "mode": "full_book"
     }'
```

3. **View API documentation:**
Open http://localhost:8000/docs in your browser for interactive API docs.

### Method 3: Using Python Requests

Create a test script:

```python
import requests

# Test endpoints
base_url = "http://localhost:8000"

# Health check
response = requests.get(f"{base_url}/health")
print(f"Health: {response.status_code}")

# Query test
data = {
    "query": "What is robotics?",
    "context_ids": [],
    "mode": "full_book"
}
response = requests.post(f"{base_url}/query", json=data)
print(f"Query: {response.status_code}")
print(response.json())
```

### Method 4: Using Postman/Insomnia

1. Import the API spec or manually create requests:
   - GET `http://localhost:8000/health`
   - POST `http://localhost:8000/query` with JSON body

### Available Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /query` - AI chatbot query (main endpoint)

### Query Endpoint Format

```json
{
  "query": "Your question here",
  "context_ids": [],  // Optional: specific content IDs
  "mode": "full_book" // or "selected_text"
}
```

### Expected Responses

**Success (200):**
```json
{
  "answer": "AI-generated answer...",
  "citations": ["Source 1", "Source 2"],
  "confidence": 0.8,
  "is_confident": true,
  "sources": ["file1.md", "file2.md"],
  "boundary_compliance": 0.9,
  "needs_fact_check": false
}
```

**Error (500):**
```json
{
  "answer": "Sorry, I'm having trouble processing your query...",
  "citations": [],
  "confidence": 0.0,
  "is_confident": false,
  "sources": [],
  "boundary_compliance": 0.0,
  "needs_fact_check": true
}
```

### Troubleshooting

1. **Server won't start:** Check for import errors in the console
2. **Query returns empty:** Vector database might be in mock mode (normal for testing)
3. **Connection errors:** Ensure no other service is using port 8000
4. **API key errors:** Set environment variables for LLM providers

### Environment Variables

Set these for full functionality:
- `OPENAI_API_KEY` - For OpenAI API
- `QDRANT_API_KEY` - For vector database
- `GEMINI_API_KEY` - For Google Gemini API
- `NEON_DATABASE_URL` - For PostgreSQL database