# Research: Replace LangChain with Direct OpenRouter LLM

**Date**: 2026-02-15 | **Branch**: `003-replace-langchain-openrouter`

## Decision 1: HTTP Client for OpenRouter

**Decision**: Use `httpx` (synchronous mode) for the OpenRouter API call.

**Rationale**: `httpx` is already in `requirements.txt` (v0.25.2) and is used in the project. It supports timeouts, JSON encoding, and proper error handling. No new dependency needed.

**Alternatives considered**:
- `requests` — Not currently in main `requirements.txt`, would add a new dependency.
- `openai` Python package — Already used in `main.py` for the OpenAI Agent path, but the Gemini fallback path in `llm_service.py` should be self-contained and not depend on the `openai` package.
- `aiohttp` — Over-engineering for a synchronous call.

## Decision 2: LangChain Removal Strategy

**Decision**: Remove all LangChain packages from all `requirements*.txt` files. Add a try/except import guard to `chunking_service.py` with inline fallback classes (mirroring the pattern already used in `content_processor.py`).

**Rationale**:
- `chunking_service.py` is the ONLY file in `backend/src/` that imports LangChain directly (line 5: `from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter`). It has NO fallback.
- `content_processor.py` already has a complete fallback implementation (lines 22-49) — a `RecursiveCharacterTextSplitter` fallback class and a `Document` class. This pattern works and is proven.
- The `chunking_service.py` fallback needs both `RecursiveCharacterTextSplitter` and `MarkdownTextSplitter`. We can create minimal inline implementations or import the existing `RecursiveCharacterTextSplitter` fallback from `content_processor.py`.

**Alternatives considered**:
- Keep `langchain-text-splitters` as a standalone package — Rejected because it still pulls in `langchain-core` which has the dependency conflicts.
- Replace chunking entirely with custom code — Out of scope, too much risk.
- Import fallback from `content_processor.py` — Viable but creates a circular dependency risk since `chunking_service.py` imports from `content_processor.py` already (line 6: `from .content_processor import ContentChunk`).

## Decision 3: LLMService Constructor Signature

**Decision**: Change `LLMService.__init__(api_key, model)` to accept an `api_key` parameter that maps to `OPENROUTER_API_KEY`, and a `model` parameter that defaults to `os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")`.

**Rationale**: The constructor signature `__init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash")` must remain compatible. Callers in `main.py` (line 341) call `LLMService(api_key=settings.gemini_api_key)`. After the change, this will still work — if `settings.gemini_api_key` is None, the service will fall back to `OPENROUTER_API_KEY` from environment.

**Alternatives considered**:
- Change the caller in `main.py` to pass `OPENROUTER_API_KEY` — Rejected because it would modify `main.py`, which is out of scope for this feature.
- Add a new constructor parameter — Rejected because it violates signature preservation (FR-003).

## Decision 4: Missing Dependencies in requirements.txt

**Decision**: Add `cohere` and `pydantic-settings` to `requirements.txt` since they are used in the code but were never listed.

**Rationale**:
- `cohere` is imported in `embedding_service.py` (line 9) but is NOT in any `requirements*.txt` file. Without it, embeddings fail.
- `pydantic-settings` is imported in `config.py` (line 1: `from pydantic_settings import BaseSettings`) but is only in `requirements_hf.txt` and `requirements_hf_optimized.txt` — NOT in main `requirements.txt`.
- These are pre-existing bugs, not new changes, but fixing them is required for the "clean install on Python 3.12" goal.

**Alternatives considered**:
- Leave them out and document as known issues — Rejected because SC-001 requires zero install errors.

## Decision 5: google-generativeai Removal

**Decision**: Remove `google-generativeai` from all requirements files since it will no longer be needed after replacing `llm_service.py` with OpenRouter.

**Rationale**: `google-generativeai` is only used in `llm_service.py` (confirmed by grep). After replacing with OpenRouter HTTP calls, this dependency is dead code. Removing it simplifies the dependency tree.

**Alternatives considered**:
- Keep it as optional — Rejected because it adds complexity and the spec mandates simplification.
