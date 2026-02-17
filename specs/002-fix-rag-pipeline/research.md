# Research: Fix RAG Pipeline

**Date**: 2026-02-15 | **Branch**: `002-fix-rag-pipeline`

## Decision 1: Import Strategy

**Decision**: Use relative imports (`from ..config import settings`) in all service files.

**Rationale**: The `main.py` uses relative imports (`from .services.vector_store`) to load services. When Python resolves this chain, all downstream imports within the package must also be relative. The `run_server.py` adds `src/` to `sys.path` which makes absolute imports work only when running standalone — but the import chain from `main.py` breaks.

**Alternatives considered**:
- Add `src/` to `sys.path` in `main.py` — rejected because it's fragile and non-standard for a package.
- Use `importlib` dynamic imports — rejected as over-engineering for a simple fix.

## Decision 2: Mock Replacement Strategy

**Decision**: Replace mock results with empty returns (vector store) or exceptions (embeddings) instead of silently degrading.

**Rationale**: Empty results propagate cleanly through the existing pipeline — `RetrievalService.retrieve_content()` already returns `[]` on error, and `main.py` already handles empty result lists by generating fallback responses. Raising exceptions in the embedding service is correct because a 10-dim mock vector would cause Qdrant dimension mismatch errors anyway.

**Alternatives considered**:
- Remove mock mode entirely from `VectorStoreService` — rejected because the `use_mock` parameter is used in constructor fallback when Qdrant connection fails; removing it would break that fallback path.
- Return zero-filled 1024-dim vectors as mock — rejected because it would return irrelevant results from Qdrant.

## Decision 3: Guardrail Approach

**Decision**: Regex-based pattern matching for injection detection + keyword topic matching for relevance.

**Rationale**: Lightweight, zero-dependency, fast (no API calls), and sufficient for the hardening phase. Can be enhanced later with ML-based classifiers.

**Alternatives considered**:
- LLM-based content filtering (send query to LLM to check safety) — rejected because it doubles API costs and adds latency.
- External guardrail service (e.g., Guardrails AI library) — rejected as over-engineering for current phase.

## Decision 4: Ingestion Script Design

**Decision**: Standalone Python script using existing services, NOT integrated into server startup.

**Rationale**: Constitution Amendment A-III rule 6 explicitly requires ingestion NOT be triggered on server startup. A standalone script gives operators full control over when to ingest content.

**Alternatives considered**:
- CLI subcommand in `main.py` — rejected because it would modify `main.py` beyond what's needed.
- Background task on first query — rejected because it would delay the first user request and violates the "not on startup" rule.

## Decision 5: Content Source for Ingestion

**Decision**: Read from `frontend/docs/` directly, excluding `tutorial-basics/` and `tutorial-extras/` directories.

**Rationale**: The `frontend/docs/` directory contains 26 markdown files across 6 topic areas (physical-ai, humanoid-robotics, vla-systems, ros2, ai-assistant, overview/intro). The tutorial-basics and tutorial-extras are Docusaurus default content about how to use Docusaurus — not textbook content.

**Files to ingest (20 files)**:
- `overview.md`, `intro.md`
- `physical-ai/introduction.md`, `physical-ai/perception.md`, `physical-ai/reasoning.md`, `physical-ai/action.md`
- `humanoid-robotics/introduction.md`, `humanoid-robotics/design.md`, `humanoid-robotics/control.md`, `humanoid-robotics/applications.md`
- `vla-systems/introduction.md`, `vla-systems/integration.md`, `vla-systems/applications.md`
- `ros2/introduction.md`, `ros2/setup.md`, `ros2/examples.md`
- `ai-assistant/using-full-book-qa.md`, `ai-assistant/using-selected-text-qa.md`, `ai-assistant/personalization.md`
