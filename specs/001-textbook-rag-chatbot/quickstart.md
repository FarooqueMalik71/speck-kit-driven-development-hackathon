# Quickstart Guide: Professional Textbook-Style RAG Chatbot

## Overview
This guide provides the essential steps to implement and run the Professional Textbook-Style RAG Chatbot with structured academic responses, conversation history, and mandatory references.

## Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Qdrant Vector Database
- OpenAI API key (or OpenRouter API key)
- PostgreSQL (Neon) for session storage (optional, in-memory for development)

## Backend Setup

### 1. Environment Configuration
```bash
cd backend
cp .env.example .env
```

Update `.env` with required values:
```env
OPENAI_API_KEY=your_openai_key_here
# OR for OpenRouter:
OPENROUTER_API_KEY=your_openrouter_key_here
LLM_PROVIDER=openrouter  # or openai
MODEL_NAME=mistralai/devstral-2512:free

QDRANT_API_KEY=your_qdrant_key
QDRANT_HOST=your_qdrant_host
QDRANT_PORT=6333

# Session storage (optional, defaults to in-memory)
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Backend Server
```bash
python start_server.py
```

The server will start on `http://localhost:8000`

## Frontend Setup

### 1. Navigate to Frontend
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start Development Server
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Usage

### Query the Textbook RAG Chatbot
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the fundamentals of Physical AI",
    "contextIds": [],
    "mode": "full_book"
  }'
```

### Start a New Conversation Session
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Physical AI?",
    "contextIds": [],
    "mode": "full_book"
  }'
```

The response will include a `sessionId` that you can use for follow-up queries.

### Continue a Conversation
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "your-session-id-from-previous-response",
    "query": "Can you elaborate on the key components?",
    "contextIds": [],
    "mode": "full_book"
  }'
```

## Key Features Implementation

### 1. Textbook-Style Responses
The system automatically formats responses with:
- Headings for major sections
- Bullet points for key concepts
- Definitions for technical terms
- Examples where appropriate
- Step-by-step explanations when needed

### 2. Mandatory References
Every concept-based query includes a "📘 Further Reading / Reference" section with:
- Internal links to relevant documents when available
- External educational resources as fallback

### 3. Polite Language Handling
The system handles ambiguous or unclear queries by:
- Detecting user intent
- Responding with "I understand your intent. Allow me to clarify it accurately."
- Providing properly formatted academic terminology

### 4. Academic Tone Enforcement
All responses follow academic standards:
- No casual language or emojis
- Structured, formal presentation
- Fact-based information from knowledge base
- No hallucinations or fabricated information

## Frontend Integration

### Chat Interface
The frontend provides:
- Textbook-style message formatting
- Conversation history panel
- Reference section display
- Creator attribution ("Built by Farooque Malik | AI-Powered RAG System")

### Styling
- Primary: Indigo
- Secondary: Soft Gray / White
- Accent: Emerald or Teal
- Clean typography with textbook-like spacing

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Configuration Options

### Response Formatting
- `STRUCTURED_RESPONSES`: Enable/disable structured formatting (default: true)
- `MAX_HISTORY_TURNS`: Maximum conversation turns to maintain (default: 10)
- `REFERENCE_REQUIRED`: Require references for all concept queries (default: true)

### Academic Tone Settings
- `ACADEMIC_TONE_ENFORCEMENT`: Enable strict academic language (default: true)
- `CASUAL_LANGUAGE_BLOCKED`: Block casual language/emojis (default: true)
- `HALLUCINATION_PREVENTION`: Strictly limit to knowledge base (default: true)

## Troubleshooting

### Common Issues
1. **API Keys**: Ensure all required API keys are properly set in `.env`
2. **Vector Database**: Verify Qdrant connection and credentials
3. **Response Format**: Check that the knowledge base has sufficient content for the queries

### Session Management
- Sessions are automatically cleaned up after TTL (configurable)
- History is maintained in memory by default (use database for production)
- Session IDs are returned in responses and should be used for follow-ups

## Next Steps
1. Ingest your academic content into the RAG system
2. Configure your knowledge base with appropriate documents
3. Test with various academic queries
4. Adjust response formatting based on feedback
5. Deploy to production environment with proper database configuration