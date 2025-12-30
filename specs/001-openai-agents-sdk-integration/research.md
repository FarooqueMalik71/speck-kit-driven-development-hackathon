# Research: OpenAI Agents SDK Integration for RAG System

## Overview
This research document outlines the key findings about the existing RAG system and how to integrate the OpenAI Agents SDK while preserving existing functionality.

## Existing System Architecture

### Current RAG Pipeline
The current RAG system consists of:
1. **RetrievalService** (`retrieval_service.py`): Handles content retrieval with relevance scoring, query expansion, and content boundary enforcement
2. **LLMService** (`llm_service.py`): Currently uses Google Gemini API for response generation
3. **Main API** (`main.py`): FastAPI endpoints for querying the textbook
4. **Configuration** (`config.py`): Settings for various services and API keys

### Key Integration Points
1. **Retrieval Service**: The existing `RetrievalService` already has methods for:
   - `retrieve_content()`: Standard content retrieval
   - `retrieve_for_selected_text_qa()`: Selected-text-only mode
   - `enforce_content_boundaries()`: Content boundary enforcement
   - `calculate_response_confidence()`: Confidence scoring

2. **Current API Flow**:
   - `/query` endpoint receives user queries
   - Retrieves content using `RetrievalService`
   - Generates response using `LLMService` (currently Gemini)
   - Applies citation generation, confidence scoring, and boundary enforcement

## OpenAI Agents SDK Integration Strategy

### Agent Design
Based on the OpenAI SDK documentation, we'll create:
1. **OpenAIAgent**: A single agent that follows official SDK patterns
2. **RAGTool**: Function tool that wraps the existing retrieval pipeline
3. **Environment-based Configuration**: For switching between OpenAI and OpenRouter

### Tool Integration
The existing `RetrievalService` will be wrapped as a function tool for the agent:
- Input: Query string and optional context_ids for selected-text mode
- Output: Retrieved content chunks with metadata
- The tool will maintain all existing functionality (relevance scoring, boundary enforcement)

### LLM Provider Configuration
New configuration will be added to support:
- `LLM_PROVIDER`: Either "openai" or "openrouter"
- `OPENAI_API_KEY`: For OpenAI provider
- `OPENROUTER_API_KEY`: For OpenRouter provider
- `MODEL_NAME`: Configurable model name

## Implementation Approach

### Phase 1: Configuration Layer
1. Update `config.py` to include new environment variables for LLM providers
2. Create a provider selector that chooses between OpenAI and OpenRouter based on configuration
3. Ensure provider switching requires no code changes

### Phase 2: Agent Construction
1. Create the OpenAI-compliant agent using official SDK patterns
2. Define system instructions that enforce content-boundary rules
3. Implement the RAG tool as a function tool using the existing retrieval service

### Phase 3: Backend Integration
1. Integrate the agent into the existing FastAPI backend
2. Update the `/query` endpoint to use the agent instead of direct LLM calls
3. Maintain backward compatibility with existing API endpoints

## Technical Considerations

### Content Boundary Enforcement
The existing `enforce_content_boundaries()` method in `RetrievalService` already handles:
- Checking if AI responses are grounded in selected content
- Calculating similarity between response and source content
- Providing boundary compliance scores

This functionality will be preserved and potentially enhanced in the agent implementation.

### Selected-Text Mode
The existing `retrieve_for_selected_text_qa()` method supports selected-text-only mode by:
- Accepting specific content IDs to search within
- Using a lower relevance threshold for this mode
- This functionality will be preserved in the agent tool.

### Error Handling
The system already has comprehensive error handling for:
- Vector store initialization failures
- API key validation failures
- Response generation errors
- These patterns will be followed in the new agent implementation.

## Dependencies to Add

### Required Dependencies
1. `openai-agents`: The official OpenAI Agents SDK
2. Potentially `litellm`: For supporting multiple providers through a unified interface

### Compatibility Requirements
1. Maintain all existing functionality in `RetrievalService`
2. Preserve existing API endpoints and response formats
3. Support both new agent-based flow and existing flow if needed for fallback

## Decision

The integration will be implemented by creating a new OpenAI-compliant agent that uses the existing `RetrievalService` as a tool. This approach preserves all existing functionality while adding the agent-based orchestration. The configuration will be environment-driven to support both OpenAI and OpenRouter providers without code changes.

## Rationale

This approach was chosen because:
1. It preserves existing RAG functionality without modification
2. It follows the OpenAI Agents SDK official patterns
3. It maintains backward compatibility
4. It allows for environment-driven provider switching
5. It enforces content-boundary rules as required

## Alternatives Considered

1. **Complete rewrite of RAG pipeline**: Rejected because it would break existing functionality
2. **Dual system (keep both Gemini and add agent)**: Would add complexity without clear benefit
3. **Direct integration without tools**: Would duplicate retrieval logic, violating the requirement not to duplicate logic

## Risks and Mitigations

1. **Performance impact**: Agent-based approach might add latency; mitigation through caching and optimization
2. **Provider availability**: Different providers may have different response formats; mitigation through standardization
3. **Configuration complexity**: Multiple API keys needed; mitigation through clear documentation