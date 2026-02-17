# AI Textbook Backend

A minimal, Hugging Face-optimized backend for the AI textbook platform.

## Features
- FastAPI-based API
- Query endpoint for textbook questions
- Health check endpoint
- Optimized for Hugging Face Spaces deployment

## Endpoints
- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /query` - Query the textbook
- `GET /test` - Test endpoint

## Environment Variables
- `GEMINI_API_KEY` - Google Gemini API key (optional for mock responses)