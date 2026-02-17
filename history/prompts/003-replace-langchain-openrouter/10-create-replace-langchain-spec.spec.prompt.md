---
id: 10
title: Create Replace LangChain OpenRouter Spec
stage: spec
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: 003-replace-langchain-openrouter
branch: 003-replace-langchain-openrouter
user: Farooque Malik
command: /sp.specify
labels: ["spec", "langchain", "openrouter", "stability", "dependencies", "llm", "python312"]
links:
  spec: specs/003-replace-langchain-openrouter/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-replace-langchain-openrouter/spec.md
  - specs/003-replace-langchain-openrouter/checklists/requirements.md
tests:
  - none
---

## Prompt

/sp.specify

TITLE: Replace LangChain with Direct OpenRouter LLM (Stability Fix)

CONTEXT: This backend project is functionally complete. RAG pipeline (Qdrant-based) is implemented, ingestion script exists, guardrails exist, API contracts and frontend integration are stable. The project currently fails due to Python dependency conflicts introduced by LangChain + langchain-openai on Python 3.12. This spec intentionally simplifies the LLM layer.

ARCHITECTURAL DECISION: We will REMOVE LangChain and langchain-openai entirely and replace ONLY the LLM call with a direct OpenRouter API call using a free, stable model: mistralai/devstral-2512:free

STRICT CONSTRAINTS (NON-NEGOTIABLE): 1. Do NOT change API endpoints, request/response schemas, RAG logic, vector store logic, ingestion logic, guardrails logic. 2. Do NOT refactor unrelated files. 3. ONLY allowed changes: requirements.txt (remove LangChain stack), llm_service.py (replace LangChain call with OpenRouter HTTP call). 4. Function signatures in llm_service.py MUST remain unchanged. 5. Environment must work on Python 3.12, Ubuntu 24.04 / WSL, HuggingFace Spaces.

GOALS: 1. Eliminate all LangChain dependencies. 2. Produce a minimal, conflict-free dependency set. 3. Ensure python ingest_textbook.py runs without ImportError. 4. Ensure backend server starts successfully. 5. Ensure chatbot produces real responses from the LLM.

## Response snapshot

Created feature specification for 003-replace-langchain-openrouter with 3 user stories (P1: clean startup, P1: real LLM responses via OpenRouter, P1: ingestion without LangChain), 10 functional requirements (FR-001 through FR-010), 7 success criteria, 5 edge cases. Deep backend analysis revealed LangChain is used in 3 files: chunking_service.py (hard dependency, NO fallback), content_processor.py (has built-in fallback classes), and requirements.txt/variants. Critical finding: chunking_service.py needs an import guard added (FR-009) since it will crash without LangChain. The openai Python package is retained because main.py's OpenAI Agent path uses it independently. Spec quality checklist: all 12 items PASS.

## Outcome

- Impact: Complete feature spec for LangChain removal with precise dependency/import analysis
- Tests: none (spec phase)
- Files: specs/003-replace-langchain-openrouter/spec.md, specs/003-replace-langchain-openrouter/checklists/requirements.md
- Next prompts: /sp.plan to create implementation plan, or /sp.clarify to refine
- Reflection: Deep import analysis before spec writing caught the chunking_service.py hard dependency that the user's original scope missed — only llm_service.py and requirements.txt were listed as allowed changes, but chunking_service.py also needs a guard. Spec documents this as FR-009.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS — all 12 checklist items validated, zero NEEDS CLARIFICATION markers
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.plan for implementation architecture
