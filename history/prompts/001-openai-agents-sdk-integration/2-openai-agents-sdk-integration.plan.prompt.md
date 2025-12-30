---
id: 2
title: OpenAI Agents SDK Integration Planning
stage: plan
date: 2025-12-27
surface: agent
model: Claude Sonnet 4.5
feature: openai-agents-sdk-integration
branch: 001-openai-agents-sdk-integration
user: Claude Code
command: /sp.plan
labels: ["plan", "openai", "agents", "rag"]
links:
  spec: specs/001-openai-agents-sdk-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-openai-agents-sdk-integration/plan.md
  - specs/001-openai-agents-sdk-integration/research.md
  - specs/001-openai-agents-sdk-integration/data-model.md
  - specs/001-openai-agents-sdk-integration/quickstart.md
  - specs/001-openai-agents-sdk-integration/contracts/api-contract.yaml
tests: []
prompt_text: |
  /sp.plan RAG Spec-3 Extension: OpenAI Agents SDK Integration

  Objective:
  Introduce a compliant OpenAI Agent using the official OpenAI Agents SDK (as defined in openAI_SDK.md) while preserving the existing RAG pipeline and enabling third-party LLM support via OpenRouter.

  Phases and Steps:

  Phase 1: Preparation and Validation
  - Read and understand openAI_SDK.md as the single source of truth
  - Identify required SDK classes, agent lifecycle, and configuration patterns
  - Audit existing RAG services to identify safe integration points
  - Confirm no changes are needed to embeddings, vector storage, or retrieval logic

  Phase 2: Configuration Layer
  - Define environment-based configuration variables:
    - LLM_PROVIDER (openai | openrouter)
    - OPENAI_API_KEY
    - OPENROUTER_API_KEY
    - MODEL_NAME
  - Implement a lightweight LLM provider selector based on configuration
  - Ensure provider switching requires no code changes

  Phase 3: Agent Construction
  - Create a single OpenAI-compliant agent following SDK patterns
  - Define agent role, system instructions, and constraints
  - Enforce content-boundary rules:
    - Answer only from retrieved chunks
    - Respect selected-text-only mode
    - Return fallback  when context is insufficient

  Phase 4: Tool Integration
  - Expose the existing retrieval pipeline as an agent tool
  - Validate correct input/output contracts between agent and retrieval service
  - Ensure metadata (citations, confidence, chunk references) is preserved

  Phase 5: Backend Integration
  - Integrate the agent into the FastAPI backend
  - Route chat requests through the agent
  - Maintain backward compatibility with existing API endpoints

  Phase 6: Testing and Validation
  - Test agent responses with:
    - Full-book queries
    - Selected-text-only queries
    - Edge cases with insufficient context
  - Verify OpenRouter and OpenAI provider switching
  - Confirm no regressions in retrieval accuracy or latency

  Phase 7: Finalization
  - Clean up unused or legacy logic if safe
  - Add minimal inline documentation for agent behavior
  - Confirm hackathon requirement alignment and readiness

  Deliverables:
  - OpenAI Agent implementation compliant with openAI_SDK.md
  - Environment-based LLM configuration with OpenRouter support
  - Fully integrated agent-driven RAG backend
  - Stable, hackathon-ready system with no core regressions

  Out of Scope:
  - Multi-agent orchestration
  - Frontend changes
  - New retrieval or ranking strategies
  - Monitoring, analytics, or billing
  - Model fine-tuning
response_text: |
  Completed the implementation plan for OpenAI Agents SDK integration with the RAG system. The plan includes:

  1. Updated implementation plan document with technical context, constitution check, and project structure
  2. Research document outlining the existing RAG system architecture and integration strategy
  3. Data model defining the key entities (OpenAIAgent, RAGTool, LLMConfiguration, etc.)
  4. Quickstart guide for setting up and using the integrated system
  5. API contract specification for the query endpoint
  6. Updated agent context with new technologies (openai-agents SDK, FastAPI)

  The plan addresses all phases from the original request:
  - Phase 0: Research completed with research.md
  - Phase 1: Data model, contracts, quickstart, and agent context completed
  - Constitution check passed with all principles verified

  The integration approach preserves existing RAG functionality while adding OpenAI agent capabilities through a function tool wrapper around the existing retrieval service.
outcome: |
  Implementation plan successfully completed with all Phase 0 and Phase 1 deliverables created. The plan provides a clear roadmap for implementing the OpenAI Agents SDK integration while preserving existing RAG functionality and supporting multiple LLM providers.
evaluation: |
  The plan comprehensively addresses the requirements with proper research, data modeling, API contracts, and quickstart documentation. The constitution check confirms compliance with project principles, and the design maintains backward compatibility while adding new agent-based capabilities.
---