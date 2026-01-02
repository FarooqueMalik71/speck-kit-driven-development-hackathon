# Hugging Face Deployment Guide for AI-Native Textbook Platform

This guide explains how to deploy the AI-Native Textbook Platform backend to Hugging Face Spaces.

## Overview

The AI-Native Textbook Platform is now optimized for Hugging Face Spaces deployment. This document provides step-by-step instructions for deploying the backend service that powers the textbook Q&A functionality.

## Prerequisites

- A Hugging Face account (https://huggingface.co/)
- Your API keys for LLM providers (Google Gemini, OpenAI, or OpenRouter)
- Git and GitHub/GitLab repository access

## Deployment Steps

### 1. Prepare Your Repository

The repository is already optimized for Hugging Face deployment with:
- `app.py` - The main application entry point
- `requirements.txt` - Dependencies for Hugging Face
- `Dockerfile.hf` - Docker configuration for Hugging Face
- Updated `README.md` - Documentation for Hugging Face users

### 2. Create a Hugging Face Space

1. Go to your Hugging Face profile
2. Click on "Spaces" in the left sidebar
3. Click "Create new Space"
4. Fill in the details:
   - Name: Choose a name for your space
   - License: Select an appropriate license
   - SDK: Select "Docker"
   - Hardware: Choose based on your needs (CPU is sufficient for development)
   - Visibility: Public or Private as per your preference

### 3. Configure Git Repository

You can deploy in one of these ways:

#### Option A: Direct Repository Upload
1. Upload this entire repository to a new Hugging Face repository
2. In the Space settings, point to this repository

#### Option B: Git Integration (Recommended)
1. Push this repository to GitHub, GitLab, or another Git provider
2. Connect your Git repository to the Hugging Face Space

### 4. Set Environment Variables

In your Hugging Face Space settings, go to the "Secrets" tab and add these environment variables:

#### Required:
- `GEMINI_API_KEY`: Your Google Gemini API key (default LLM provider)

#### Optional (for alternative LLM providers):
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `LLM_PROVIDER`: Set to "gemini", "openai", or "openrouter" (default: "gemini")
- `MODEL_NAME`: Specific model name to use (default: "mistralai/devstral-2512:free")

### 5. Configure the Space

The Space is configured with:
- Docker SDK (using `Dockerfile.hf`)
- FastAPI application (using `app.py`)
- Port 7860 (Hugging Face standard)

### 6. Build and Deploy

Once you've configured the repository and environment variables:
1. The Space will automatically start building
2. Monitor the build logs in the "Logs" tab
3. Wait for the build to complete (this may take several minutes)
4. Once built, your API will be available at: `https://[your-username]-[space-name].hf.space`

## API Usage

Once deployed, your API endpoints will be available:

### Health Check
```
GET https://[your-username]-[space-name].hf.space/
```

### Query Endpoint
```
POST https://[your-username]-[space-name].hf.space/query
Content-Type: application/json

{
  "query": "Your question about the textbook",
  "context_ids": [],
  "mode": "full_book"
}
```

### Example Response
```json
{
  "answer": "Detailed answer to your question...",
  "citations": ["Chapter 1", "Section 2.3"],
  "confidence": 0.85,
  "is_confident": true,
  "sources": ["textbook_chapter_1", "textbook_chapter_2"],
  "boundary_compliance": 0.92,
  "needs_fact_check": false
}
```

## Troubleshooting

### Common Issues:

1. **Build Failures**: Check the logs for dependency installation issues. The requirements.txt is optimized for Hugging Face.

2. **API Key Issues**: Ensure your API keys are set in the Space secrets and match the expected environment variable names.

3. **Timeout Issues**: Hugging Face Free tier has limitations. Consider upgrading for production use.

4. **Memory Issues**: The application may require more memory for large vector operations. Consider using a higher-tier hardware option.

### Checking Logs:
- Go to your Space page
- Click on the "Logs" tab
- Check both build logs and runtime logs

## Architecture Notes

- The backend uses FastAPI for high-performance API serving
- RAG (Retrieval-Augmented Generation) functionality is available
- Multiple LLM providers are supported
- Vector storage is configured for Qdrant (cloud or local)
- The application includes hallucination prevention and content boundary enforcement

## Updating the Deployment

To update your deployment:
1. Push changes to your connected Git repository
2. Or update files directly in the Hugging Face repository
3. The Space will automatically rebuild
4. Monitor the build logs for successful deployment

## Resource Considerations

- **CPU Spaces**: Suitable for development and light usage
- **GPU Spaces**: Recommended for better performance with larger models
- **Hardware**: Start with CPU, upgrade as needed based on usage

## Security

- API keys are stored securely in Hugging Face secrets
- CORS is configured to allow necessary origins
- Input validation is implemented in the API endpoints
- No sensitive data is stored in the application

## Cost Considerations

- Free tier: Limited compute time
- Paid tier: More compute time and better hardware options
- Consider your expected usage when choosing a plan

## Support

If you encounter issues:
1. Check the Hugging Face Space logs
2. Verify your environment variables
3. Ensure dependencies in requirements.txt are compatible
4. Test locally before deploying if making changes