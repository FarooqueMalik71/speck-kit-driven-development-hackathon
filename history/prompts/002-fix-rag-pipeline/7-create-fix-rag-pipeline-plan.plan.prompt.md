---
id: 7
title: Create Fix RAG Pipeline Plan
stage: plan
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: 002-fix-rag-pipeline
branch: 002-fix-rag-pipeline
user: Farooque Malik
command: /sp.plan
labels: ["plan", "rag", "pipeline", "fix", "imports", "guardrails", "ingestion"]
links:
  spec: specs/002-fix-rag-pipeline/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fix-rag-pipeline/plan.md
  - specs/002-fix-rag-pipeline/research.md
  - specs/002-fix-rag-pipeline/quickstart.md
tests:
  - none
---

## Prompt

/sp.plan

PLANNING MODE: Restricted debugging and hardening phase. Fix behavior, not redesign. Prefer minimal surgical changes. 10-step plan covering: repository reconnaissance, mock detection, Qdrant reality check, drop-in replacement design, textbook ingestion strategy, silent failure fixes, guardrail integration, environment safety validation, verification planning, and change documentation.

## Response snapshot

Created comprehensive implementation plan with 9 surgical changes across 10 files (8 modified, 2 new). Key findings: (1) Root cause of mock behavior is broken absolute imports in vector_store.py, embedding_service.py, content_processor.py — when main.py uses relative imports, the chain breaks and services fall back to mock mode. (2) 6 mock code locations identified with exact line numbers. (3) Plan preserves all function signatures, API contracts, and folder structure per Amendment A. (4) New files: guardrails.py (regex-based injection detection) and ingest_textbook.py (standalone, never auto-runs). (5) 5 research decisions documented. (6) 4-step verification plan with curl commands. (7) Execution order: imports → mock removal → security → guardrails → ingestion → verification.

## Outcome

- Impact: Complete implementation plan for RAG pipeline fix with line-level precision
- Tests: none (plan phase)
- Files: plan.md, research.md, quickstart.md
- Next prompts: /sp.tasks to generate actionable task list, or /sp.implement to begin execution
- Reflection: Deep import chain analysis revealed the root cause — not a mock design problem but an import resolution failure that cascades into mock fallbacks. The fix is elegant: 5 import path changes unblock the entire service chain.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS — all constitution gates checked, no unresolved clarifications
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement Change 1 (imports) first to validate the cascade fix theory
