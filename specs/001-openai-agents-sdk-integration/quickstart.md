# Quickstart Guide: OpenAI Agents SDK Integration for RAG System

## Overview
This guide provides instructions for setting up and using the OpenAI Agents SDK integration with the existing RAG system.

## Prerequisites
- Python 3.11+
- Access to OpenAI API or OpenRouter API
- Existing RAG system with vector store (Qdrant) running
- Environment variables configured

## Installation

### 1. Install Dependencies
```bash
pip install openai-agents
```

### 2. Environment Configuration
Set up the required environment variables:

For OpenAI provider:
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_openai_api_key_here
export MODEL_NAME=gpt-4o  # or other supported model
```

For OpenRouter provider:
```bash
export LLM_PROVIDER=openrouter
export OPENROUTER_API_KEY=your_openrouter_api_key_here
export MODEL_NAME=openai/gpt-4o  # or other supported model
```

### 3. Configuration in config.py
The system will automatically detect the provider from environment variables and configure accordingly.

## Usage

### 1. Starting the Service
The agent integration is automatically enabled when you start the FastAPI service:

```bash
cd backend
python -m src.main
```

### 2. Making Queries
The existing `/query` endpoint now uses the OpenAI agent:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is embodied intelligence?",
    "mode": "full_book"
  }'
```

For selected-text mode:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the key concepts",
    "context_ids": ["chunk_id_1", "chunk_id_2"],
    "mode": "selected_text"
  }'
```

### 3. Switching Providers
To switch between OpenAI and OpenRouter, simply change the environment variables and restart the service:
- Set `LLM_PROVIDER=openai` and `OPENAI_API_KEY` for OpenAI
- Set `LLM_PROVIDER=openrouter` and `OPENROUTER_API_KEY` for OpenRouter

No code changes are required.

## Key Features

### Content Boundary Enforcement
The agent enforces content boundaries by:
- Only responding based on retrieved document chunks
- Providing boundary compliance scores
- Indicating when fact-checking is needed

### Selected-Text Mode
When context_ids are provided, the agent will:
- Only use the specified content chunks
- Respond exclusively based on the provided text
- Maintain strict adherence to the selected content

### Confidence Scoring
Responses include confidence metrics:
- Overall confidence in the response
- Boundary compliance score
- Indication of whether fact-checking is needed

## Troubleshooting

### Provider Not Working
- Verify the correct API key is set for the selected provider
- Check that `LLM_PROVIDER` environment variable matches your API key type
- Confirm the model name is supported by your selected provider

### Content Boundary Issues
- If responses seem to hallucinate, verify that retrieval is working correctly
- Check that retrieved chunks have sufficient relevance scores
- Ensure the query is specific enough to retrieve relevant content

### Performance Issues
- Large queries may take longer to process
- First-time queries might be slower due to agent initialization
- Consider implementing caching for frequently asked questions