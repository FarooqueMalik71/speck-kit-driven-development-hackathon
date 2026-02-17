---
id: 11
title: Create Replace LangChain Plan
stage: plan
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: 003-replace-langchain-openrouter
branch: 003-replace-langchain-openrouter
user: Farooque Malik
command: /sp.plan
labels: ["plan", "langchain", "openrouter", "stability", "dependencies", "httpx", "chunking"]
links:
  spec: specs/003-replace-langchain-openrouter/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-replace-langchain-openrouter/plan.md
  - specs/003-replace-langchain-openrouter/research.md
  - specs/003-replace-langchain-openrouter/quickstart.md
tests:
  - none
---

## Prompt

/sp.plan

OBJECTIVE: Stabilize the backend by removing LangChain dependencies and replacing the LLM call with a direct OpenRouter API integration, without affecting existing RAG logic, API contracts, or frontend behavior.

SCOPE: Backend only, dependency and LLM service layer only, no changes to API schemas or endpoints.

PLAN OVERVIEW: Phase 1 — Dependency Simplification (remove LangChain), Phase 2 — LLM Service Replacement (OpenRouter via httpx), Phase 3 — Error Handling & Safety, Phase 4 — Environment Validation, Phase 5 — Testing & Verification.

## Response snapshot

Created comprehensive implementation plan with 4 surgical changes across 6 files (3 code files modified, 3 requirements files cleaned). Key findings from deep analysis: (1) LangChain is only imported in 2 backend/src files — chunking_service.py (NO fallback, will crash) and content_processor.py (HAS fallback). (2) google.generativeai only used in llm_service.py. (3) cohere package is MISSING from all requirements.txt files despite being used in embedding_service.py. (4) pydantic-settings MISSING from main requirements.txt despite being imported in config.py. (5) LLMService is called from 3 files: main.py (active), rag_service.py, chatbot.py — all use generate_response_with_citations(). 5 research decisions documented. 5-step verification plan with commands. Execution order: dependencies → LLM service → import guard → verification.

## Outcome

- Impact: Complete implementation plan for LangChain removal with exact code diffs and dependency analysis
- Tests: none (plan phase)
- Files: plan.md, research.md, quickstart.md
- Next prompts: /sp.tasks to generate task list, or /sp.implement to begin execution
- Reflection: Deep dependency analysis revealed 2 pre-existing bugs (missing cohere and pydantic-settings in requirements.txt) that would cause the "clean install" success criterion to fail even without the LangChain change. The chunking_service.py crash risk was the critical discovery — without the import guard, removing LangChain would break the entire server import chain.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS — all constitution gates checked, all files mapped
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.tasks then /sp.implement to execute the 4 changes
