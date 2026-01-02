# Physical AI & Humanoid Robotics — An AI-Native Textbook for Embodied Intelligence

This is an AI-native textbook platform that combines traditional textbook content with AI-powered interactive features. The system provides a Docusaurus-based frontend with embedded AI capabilities including RAG (Retrieval-Augmented Generation) chatbot, personalization, and translation services.

## Project Structure

```
├── backend/                 # FastAPI backend services
│   ├── src/
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   ├── api/            # API endpoints
│   │   └── agents/         # AI agents
│   └── tests/
├── frontend/               # Docusaurus textbook frontend
│   ├── docs/              # Textbook content
│   ├── src/               # Custom components
│   ├── static/            # Static assets
│   └── docusaurus.config.ts
├── api/                    # Vercel-ready serverless API endpoints
├── specs/                  # Project specifications
└── app.py                  # Hugging Face Spaces entry point
```

## Tech Stack

- **Frontend**: Docusaurus (for textbook content)
- **Backend**: FastAPI (Python 3.11)
- **AI/ML**: OpenAI API, LangChain
- **Vector DB**: Qdrant Cloud
- **Relational DB**: Neon Serverless Postgres
- **Authentication**: Better-Auth
- **Deployment**: Vercel (frontend), Hugging Face Spaces (backend)

## Hugging Face Deployment

This application is ready for deployment on Hugging Face Spaces using the FastAPI runtime.

### Environment Variables

The following environment variables need to be set in Hugging Face Spaces:

- `GEMINI_API_KEY`: Your Google Gemini API key (for default model)
- `OPENAI_API_KEY`: Your OpenAI API key (optional, for OpenAI models)
- `OPENROUTER_API_KEY`: Your OpenRouter API key (optional, for OpenRouter models)
- `LLM_PROVIDER`: Which LLM provider to use ("gemini", "openai", or "openrouter")
- `MODEL_NAME`: Model name to use (default: "mistralai/devstral-2512:free")

### API Endpoints

- `GET /`: Health check endpoint
- `GET /health`: Health status
- `POST /query`: Query the textbook with your question

### Query Format

Send a POST request to `/query` with JSON body:

```json
{
  "query": "Your question about the textbook",
  "context_ids": [],
  "mode": "full_book"
}
```

## Local Development

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements_basic.txt
   ```

4. Set up environment variables:
   - Copy `backend/.env.example` to `backend/.env` and fill in your API keys
   - Required variables:
     - `GEMINI_API_KEY`: Your Google Gemini API key
     - `OPENAI_API_KEY`: Your OpenAI API key (optional)
     - `OPENROUTER_API_KEY`: Your OpenRouter API key (optional)
     - `LLM_PROVIDER`: LLM provider to use ("gemini", "openai", or "openrouter")
     - `MODEL_NAME`: Model name to use

5. Start the backend server:
   ```bash
   python run_server.py
   ```
   The server will be available at http://localhost:8000

### Frontend (Textbook) Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Access the AI chat interface at:
   - Main site: http://localhost:3000
   - AI Chat: http://localhost:3000/ai-chat

## Features

- AI-powered Q&A with full-book and selected-text modes
- Personalized learning paths
- Real-time translation (including Urdu)
- Content boundary enforcement to prevent information leakage
- Hallucination prevention mechanisms
- User progress tracking
- Interactive textbook components

## Development

This project follows a specification-driven development approach. All features are documented in the `specs/` directory with:
- `spec.md` - Technical specification
- `plan.md` - Implementation plan
- `tasks.md` - Detailed task breakdown

## Contributing

1. Follow the task breakdown in `specs/1-ai-textbook/tasks.md`
2. Implement features following the architecture in `plan.md`
3. Ensure all tests pass before submitting changes
4. Update documentation as needed