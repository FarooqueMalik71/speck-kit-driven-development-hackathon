---
id: 6
title: Create Fix RAG Pipeline Spec
stage: spec
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: 002-fix-rag-pipeline
branch: 002-fix-rag-pipeline
user: Farooque Malik
command: /sp.specify
labels: ["spec", "rag", "pipeline", "fix", "qdrant", "chatbot", "guardrails"]
links:
  spec: specs/002-fix-rag-pipeline/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fix-rag-pipeline/spec.md
  - specs/002-fix-rag-pipeline/checklists/requirements.md
tests:
  - none
---

## Prompt

/sp.spec

PROJECT CONTEXT:
This project is an AI-native textbook platform for Physical AI & Humanoid Robotics.
The frontend (Docusaurus on Vercel) and backend (FastAPI on Hugging Face Spaces)
are already deployed and functioning.

The chatbot currently responds using mock or simulated RAG logic.
The goal of this specification is to replace simulated behavior
with a real, production-safe Retrieval-Augmented Generation (RAG) pipeline.

This specification operates under:
- Constitution v1.0.0
- Constitution Amendment: Debugging & Hardening Phase

GOAL:
Fix the chatbot so that all answers are generated strictly
from real textbook content using a Qdrant-based RAG pipeline,
without breaking or restructuring the existing system.

SCOPE (STRICT):
- Backend ONLY
- No frontend changes
- No API route changes
- No renaming of existing files or folders

IN-SCOPE OBJECTIVES:
1. Identify all mock, fake, or placeholder RAG logic in the backend.
2. Replace mock vector search with real Qdrant similarity search.
3. Preserve existing function names, parameters, return formats.
4. Ensure chatbot context comes ONLY from textbook content.
5. Add a one-time ingestion script.
6. Ensure ingestion is NOT triggered automatically on server startup.
7. Fix silent failures.
8. Remove fake or default API key fallbacks.
9. Add basic chatbot guardrails to prevent misuse.

OUT-OF-SCOPE: architecture redesign, service rewrites, authentication, frontend changes, new databases, breaking validation rules.

RAG REQUIREMENTS: Use existing Qdrant config, real embeddings, top-k retrieval, safe fallback on no context.

GUARDRAILS: Refuse non-textbook queries, ignore system override attempts, reject prompt injection, avoid unsafe responses.

VERIFICATION: Backend startup, no mock data paths, frontend compatibility, chatbot behavior tests.

## Response snapshot

Created feature specification for 002-fix-rag-pipeline with 4 user stories (P1: textbook Q&A, P1: content ingestion, P2: prompt injection prevention, P2: eliminate silent failures), 10 functional requirements (FR-001 through FR-010), 7 measurable success criteria, 5 edge cases, and clear scope boundaries. Deep backend analysis identified 6 exact mock/fake code locations: mock embeddings in embedding_service.py, mock search in vector_store.py, mock LLM responses in llm_service.py and main.py, fake API keys in run_server.py and start_server.py. All 26 textbook markdown files in frontend/docs/ identified as ingestion source. Spec quality checklist created and all items pass validation. No clarifications needed.

## Outcome

- Impact: Complete feature spec created for RAG pipeline fix with precise mock identification
- Tests: none (spec phase)
- Files: specs/002-fix-rag-pipeline/spec.md, specs/002-fix-rag-pipeline/checklists/requirements.md
- Next prompts: /sp.plan to create implementation plan, or /sp.clarify to refine
- Reflection: Deep code analysis before spec writing ensured all mock paths were precisely identified; zero NEEDS CLARIFICATION markers needed because the user provided comprehensive scope

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS - all checklist items validated
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.plan for implementation architecture
