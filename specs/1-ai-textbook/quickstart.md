# Quickstart Guide: AI-Native Textbook Platform

## Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- Docker and Docker Compose (for local development)
- OpenAI API key
- Qdrant Cloud account and API key
- Neon Postgres account and connection string

## Local Development Setup

### 1. Clone and Initialize Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys and connection strings
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install

# Set environment variables
cp .env.example .env
# Edit .env with your API endpoints and keys
```

### 4. Documentation Setup

```bash
# Navigate to docs directory
cd docs

# Install dependencies
npm install
# or
yarn install
```

## Environment Configuration

Create `.env` files in both backend and frontend with the following variables:

### Backend (.env)
```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_HOST=your_qdrant_cluster_url
NEON_DATABASE_URL=your_neon_postgres_connection_string
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key
```

### Frontend (.env)
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_OPENAI_API_KEY=your_openai_api_key
REACT_APP_QDRANT_HOST=your_qdrant_cluster_url
```

## Running the Application

### Development Mode

#### Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm start
# or
yarn start
```

#### Documentation (Docusaurus)
```bash
cd docs
npm start
# or
yarn start
```

### Using Docker Compose (Recommended for local development)
```bash
docker-compose up --build
```

## API Contract Overview

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user info

### Content Endpoints
- `GET /content/` - List textbook content
- `GET /content/{id}` - Get specific content
- `GET /content/search` - Search content

### AI Endpoints
- `POST /ai/qa` - Full-book Q&A
- `POST /ai/qa-selected` - Selected-text Q&A
- `POST /ai/translate` - Content translation

### User Endpoints
- `GET /user/progress` - User progress
- `POST /user/progress` - Update progress
- `GET /user/notes` - User notes
- `POST /user/notes` - Create/update notes

## Database Migrations

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

## Running Tests

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
# or
yarn test
```

## Content Management

### Adding New Textbook Content
1. Create markdown files in `docs/docs/` directory
2. Update `docs/sidebars.js` to include new content in navigation
3. Run content indexing script to update vector store:

```bash
cd backend
python -m src.scripts.index_content
```

## Deployment

### To Vercel
```bash
# Frontend
vercel --prod

# Backend (as serverless functions)
vercel --prod --functions backend/src/api
```

### Environment Variables for Production
Set the same environment variables in your Vercel project settings as in your local `.env` files.

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Check your OpenAI usage and adjust request frequency
2. **Database Connection**: Verify Neon Postgres connection string and credentials
3. **Vector Store**: Ensure Qdrant cluster is accessible and API key is correct
4. **CORS Issues**: Check backend CORS configuration for frontend URL

### Useful Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Check AI service connectivity
curl http://localhost:8000/ai/health

# View all environment variables
printenv | grep -E "(OPENAI|QDRANT|NEON)"
```