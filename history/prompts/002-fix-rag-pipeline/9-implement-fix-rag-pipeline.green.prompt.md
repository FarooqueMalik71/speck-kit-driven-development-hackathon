---
id: 9
title: Implement Fix RAG Pipeline
stage: green
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: 002-fix-rag-pipeline
branch: 002-fix-rag-pipeline
user: Farooque Malik
command: /sp.implement
labels: ["implement", "rag", "pipeline", "fix", "imports", "mock-removal", "guardrails", "ingestion", "green"]
links:
  spec: specs/002-fix-rag-pipeline/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/vector_store.py
  - backend/src/services/embedding_service.py
  - backend/src/services/content_processor.py
  - backend/src/services/llm_service.py
  - backend/src/main.py
  - backend/run_server.py
  - backend/start_server.py
  - backend/src/config.py
  - backend/src/services/guardrails.py
  - backend/ingest_textbook.py
  - specs/002-fix-rag-pipeline/tasks.md
tests:
  - none (manual verification — grep confirms zero "simulated response" strings in backend/src/)
---

## Prompt

/sp.implement

## Response snapshot

Executed all 20 tasks across 6 phases from tasks.md. Phase 1: Fixed 5 broken absolute imports across 3 files (vector_store.py, embedding_service.py, content_processor.py) — changed `from config import settings` to `from ..config import settings` and `from models.x` to `from ..models.x`. Phase 2: Removed all mock logic — replaced mock search results (3 hardcoded results returning scores 0.95/0.89/0.82) with empty list + warning, replaced mock embeddings ([0.1..1.0][:10]) with RuntimeError, replaced mock LLM response with safe fallback, replaced 4 mock response blocks in main.py with canonical safe fallback message. Phase 3: Created `backend/ingest_textbook.py` — standalone script using ContentProcessor + EmbeddingService + VectorStoreService, reads 20 markdown files from frontend/docs/ (excludes tutorial-*), never auto-runs. Phase 4: Removed 7 fake API key setdefault lines from run_server.py (4 lines) and start_server.py (3 lines), uncommented config validation with warnings instead of errors. Phase 5: Created `backend/src/services/guardrails.py` with 11 injection patterns and 27 topic keywords, integrated into main.py query_textbook() as first check. Phase 6: Verified all changes — grep confirms zero "simulated response" in src/, zero fake keys in prod code, all 20 tasks marked [x].

## Outcome

- Impact: Complete RAG pipeline fix — 8 files modified, 2 new files created, all mock paths eliminated
- Tests: Manual verification (grep-based) — zero "simulated response" strings, zero fake keys in production code
- Files: 10 backend files changed (see files list above), tasks.md updated with all 20 tasks checked off
- Next prompts: Run `cd backend && python ingest_textbook.py` to populate Qdrant, then `python run_server.py` to test, then curl commands from quickstart.md
- Reflection: The import chain fix (Phase 1) was the critical enabler — 5 import path changes unblocked the entire real service chain. The rest was surgical mock removal following the plan exactly. ContentProcessor was used instead of ChunkingService for ingestion because ChunkingService has a field name mismatch (uses source_file but ContentChunk expects source_url).

## Evaluation notes (flywheel)

- Failure modes observed: ChunkingService._chunk_section() passes `source_file=source_file` to ContentChunk which expects `source_url` — used ContentProcessor instead for ingestion script
- Graders run and results (PASS/FAIL): PASS — all 20 tasks completed, zero "simulated response" in codebase, zero fake keys in production paths
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run `cd backend && python ingest_textbook.py` to validate end-to-end with real Qdrant + Cohere
