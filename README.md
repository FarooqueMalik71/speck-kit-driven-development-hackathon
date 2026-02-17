# AI-Native Textbook Platform for Physical AI & Humanoid Robotics

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Docusaurus](https://img.shields.io/badge/docusaurus-3.0-blue.svg)](https://docusaurus.io/)

## 🤖 Overview

This is an AI-native textbook platform that revolutionizes learning through interactive AI-powered features. The system combines traditional textbook content with cutting-edge AI capabilities including Retrieval-Augmented Generation (RAG) chatbot, personalized learning paths, and real-time translation services.

**Live Demo**:
- Frontend (Vercel): [https://speck-kit-driven-development-hackat-nine.vercel.app/](https://speck-kit-driven-development-hackat-nine.vercel.app/ai-chat)
- Backend (Hugging Face Spaces): [https://huggingface.co/spaces/farooquemalik50871/AI-Book-Backend](https://huggingface.co/spaces/farooquemalik50871/AI-Book-Backend)

## ✨ Key Features

- **AI-Powered Q&A**: Intelligent chatbot with full-book and selected-text query modes
- **RAG Implementation**: Retrieval-Augmented Generation for accurate, context-aware responses
- **Personalized Learning**: Adaptive learning paths based on user interactions
- **Real-time Translation**: Multi-language support including Urdu translation
- **Content Boundary Enforcement**: Prevents information leakage and maintains content integrity
- **Hallucination Prevention**: Advanced mechanisms to ensure factual accuracy
- **Interactive Components**: Engaging textbook elements with AI integration
- **User Progress Tracking**: Monitor learning progress and achievements

## 🏗️ Architecture

```
├── backend/                 # FastAPI backend services
│   ├── src/
│   │   ├── models/         # Pydantic data models
│   │   ├── services/       # Business logic and AI services
│   │   ├── api/            # API endpoints (v1)
│   │   ├── agents/         # AI agent implementations
│   │   └── config/         # Configuration and settings
│   ├── tests/              # Backend test suite
│   └── requirements.txt    # Python dependencies
├── frontend/               # Docusaurus textbook frontend
│   ├── docs/              # Textbook content in Markdown
│   ├── src/               # Custom React components
│   ├── static/            # Static assets and images
│   ├── pages/             # Custom page components
│   └── docusaurus.config.ts # Docusaurus configuration
├── specs/                  # Project specifications and documentation
├── history/                # Prompt history and ADRs
├── app.py                  # Hugging Face Spaces entry point
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Backend Docker configuration
└── README.md               # This file
```

## 🛠 Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework
- **Language**: Python 3.11
- **AI/ML**: [LangChain](https://python.langchain.com/), [OpenAI API](https://platform.openai.com/), [Google Gemini](https://ai.google.dev/)
- **Vector Database**: [Qdrant](https://qdrant.tech/) - Cloud vector database
- **Relational DB**: [Neon](https://neon.tech/) Serverless Postgres
- **Authentication**: [Better-Auth](https://www.better-auth.com/)

### Frontend
- **Framework**: [Docusaurus](https://docusaurus.io/) - Static site generator
- **Language**: TypeScript/JavaScript
- **Styling**: CSS Modules, Tailwind CSS
- **Deployment**: [Vercel](https://vercel.com/)

### Deployment
- **Frontend**: [Vercel](https://vercel.com/) - Global CDN deployment
- **Backend**: [Hugging Face Spaces](https://huggingface.co/spaces) - GPU-accelerated inference

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn
- Git

### Backend Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd hackathon-project
```

2. Navigate to the backend directory:
```bash
cd backend
```

3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
   - Copy `.env.example` to `.env` and fill in your API keys
   - Required variables:
     - `GEMINI_API_KEY`: Your Google Gemini API key
     - `OPENAI_API_KEY`: Your OpenAI API key (optional)
     - `OPENROUTER_API_KEY`: Your OpenRouter API key (optional)
     - `QDRANT_API_KEY`: Your Qdrant vector database key
     - `NEON_DATABASE_URL`: Your Neon Postgres connection string

6. Start the backend server:
```bash
python run_server.py
```
The server will be available at http://localhost:8000

### Frontend Setup
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

4. Access the application at:
- Main site: http://localhost:3000
- AI Chat: http://localhost:3000/ai-chat

## 📚 API Documentation

### Backend Endpoints
- `GET /` - Health check endpoint
- `GET /health` - Health status
- `POST /query` - Query the textbook with your question
- `GET /session/{session_id}` - Retrieve conversation history
- `GET /capabilities` - AI capabilities information

### Query Format
Send a POST request to `/query` with JSON body:
```json
{
  "query": "Your question about the textbook",
  "context_ids": [],
  "mode": "full_book"
}
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow the specification-driven development approach
- All features are documented in the `specs/` directory
- Write tests for new functionality
- Follow existing code style and patterns
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📈 Project Status

- ✅ Core AI functionality implemented
- ✅ RAG system operational
- ✅ Frontend integration complete
- ✅ Multi-language support
- ✅ Deployment ready
- 🔄 Continuous improvements and feature additions

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## 🙏 Acknowledgments

- Special thanks to the open-source community for the amazing tools and libraries
- Google Gemini, OpenAI, and other AI providers for their APIs
- The Docusaurus and FastAPI teams for their excellent frameworks
- All contributors who help make this project better

---

<p align="center">
  Made with ❤️ for the AI Education Community
</p>