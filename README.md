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
└── specs/                  # Project specifications
    └── 1-ai-textbook/     # Current feature specs
```

## Tech Stack

- **Frontend**: Docusaurus (for textbook content)
- **Backend**: FastAPI (Python 3.11)
- **AI/ML**: OpenAI API, LangChain
- **Vector DB**: Qdrant Cloud
- **Relational DB**: Neon Serverless Postgres
- **Authentication**: Better-Auth
- **Deployment**: Vercel

## Setup

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
   pip install -r requirements.txt
   ```

4. Set up environment variables (copy `.env.example` to `.env` and fill in values)

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