---
id: 13
title: Implement Replace LangChain OpenRouter
stage: green
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: 003-replace-langchain-openrouter
branch: 003-replace-langchain-openrouter
user: Farooque Malik
command: /sp.implement
labels: ["implement", "langchain", "openrouter", "httpx", "dependencies", "chunking", "llm"]
links:
  spec: specs/003-replace-langchain-openrouter/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/requirements.txt
  - backend/requirements_hf.txt
  - backend/requirements_hf_optimized.txt
  - backend/requirements_basic.txt
  - backend/src/services/llm_service.py
  - backend/src/services/chunking_service.py
  - backend/src/services/vector_store.py
  - backend/src/services/embedding_service.py
  - specs/003-replace-langchain-openrouter/tasks.md
tests:
  - T007 pip install zero errors PASS
  - T008 langchain absence PASS
  - T009 import verification PASS
  - T010 ingestion 19 files 116 chunks PASS
  - T011 backend startup PASS
  - T012 valid textbook query PASS
  - T013 prompt injection refused PASS
  - T014 fallback with bad key PASS
  - T015 frontend build PASS
---

## Prompt

/sp.implement

## Response snapshot

Executed all 15 tasks across 4 phases for feature 003-replace-langchain-openrouter. Phase 1: Cleaned 4 requirements files — removed all LangChain, google-generativeai, SQLAlchemy, pytest; added missing cohere and pydantic-settings. Phase 2: Rewrote llm_service.py — replaced Gemini with OpenRouter via httpx, preserved all 5 method signatures exactly. Phase 3: Added LangChain import guard to chunking_service.py with inline fallback RecursiveCharacterTextSplitter and MarkdownTextSplitter classes. Phase 4: All 9 verification tests passed. Also fixed 3 pre-existing bugs discovered during verification: vector_store.py check_compatibility kwarg, Qdrant Cloud URL handling, and embedding_service.py missing env var fallback.

## Outcome

- Impact: LangChain fully removed from backend. OpenRouter LLM integration working end-to-end. Clean Python 3.12 install with zero dependency conflicts.
- Tests: 9/9 verification tests PASS (pip install, langchain absence, imports, ingestion, startup, valid query, injection, fallback, frontend build)
- Files: 8 files modified (6 planned + 2 pre-existing bug fixes), tasks.md updated with all checkmarks
- Next prompts: /sp.git.commit_pr to commit and create PR, or manual testing with additional queries
- Reflection: The planned 6-file change was clean and surgical. However, end-to-end verification exposed 3 pre-existing bugs (vector_store.py check_compatibility, Qdrant URL handling, embedding_service env var) that were blocking the query pipeline. These were minimal isolated fixes consistent with Amendment A. The default free model on OpenRouter had expired (devstral-2512:free), requiring a switch to google/gemma-3-4b-it:free.

## Evaluation notes (flywheel)

- Failure modes observed: (1) qdrant-client 1.8.0 doesn't support check_compatibility kwarg, (2) Qdrant Cloud URL needs https:// prefix with url= param, (3) EmbeddingService didn't read COHERE_API_KEY from env, (4) Default OpenRouter model expired
- Graders run and results (PASS/FAIL): PASS — all 15 tasks completed, all 9 verification tests pass
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Commit all changes and create PR for review
