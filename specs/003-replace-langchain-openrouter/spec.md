# Feature Specification: Replace LangChain with Direct OpenRouter LLM (Stability Fix)

**Feature Branch**: `003-replace-langchain-openrouter`
**Created**: 2026-02-15
**Status**: Draft
**Constitution**: v1.1.0 (Amendment A: Debugging & Hardening Phase active)
**Input**: User description: "Replace LangChain with Direct OpenRouter LLM call to eliminate Python dependency conflicts on Python 3.12."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Backend Starts Without Dependency Errors (Priority: P1)

An operator deploys the backend on Python 3.12 (Ubuntu 24.04 / WSL / HuggingFace Spaces). The dependency installation succeeds with zero resolution conflicts, and the server starts without ImportError or ModuleNotFoundError.

**Why this priority**: If dependencies cannot install cleanly, nothing else works. This is the root blocker that prompted this feature.

**Independent Test**: Run `pip install -r requirements.txt` on a clean Python 3.12 environment, then `python run_server.py`. Both must succeed with no errors.

**Acceptance Scenarios**:

1. **Given** a clean Python 3.12 virtual environment, **When** `pip install -r requirements.txt` is run, **Then** all packages install with zero dependency resolution errors.
2. **Given** dependencies are installed, **When** `python run_server.py` is started, **Then** the server binds to `0.0.0.0:8000` without ImportError.
3. **Given** the server is running, **When** `pip list | grep langchain` is executed, **Then** zero LangChain packages appear.

---

### User Story 2 — Chatbot Produces Real LLM Responses via OpenRouter (Priority: P1)

A student asks a textbook question. The backend retrieves relevant content from Qdrant, sends it to OpenRouter's `mistralai/devstral-2512:free` model via a direct HTTP call, and returns a grounded answer — not a mock or fallback response.

**Why this priority**: The chatbot's core value proposition requires real LLM-generated answers from retrieved textbook context. This is the functional replacement for the removed Gemini/LangChain LLM path.

**Independent Test**: Start the backend with a valid `OPENROUTER_API_KEY`, run `curl POST /query {"query": "What is Physical AI?"}`, and verify the response contains a substantive answer (not the safe fallback message).

**Acceptance Scenarios**:

1. **Given** the backend is running with a valid `OPENROUTER_API_KEY`, **When** a student asks "What is Physical AI?", **Then** the response contains a substantive answer derived from textbook content.
2. **Given** the backend is running, **When** the `LLMService.generate_response()` method is called with context, **Then** it makes an HTTP POST to `https://openrouter.ai/api/v1/chat/completions` and returns the model's text.
3. **Given** the OpenRouter API returns an error, **When** the LLM call fails, **Then** the system returns the safe fallback message: "I can only answer questions based on the Physical AI & Humanoid Robotics textbook."

---

### User Story 3 — Ingestion Script Runs Without LangChain (Priority: P1)

An operator runs `python ingest_textbook.py` to populate the Qdrant vector store. The script must work without LangChain installed, since `content_processor.py` (used by the ingestion script) has built-in fallback text splitting classes.

**Why this priority**: Without successful ingestion, the RAG pipeline has no content to retrieve. The ingestion path must survive the LangChain removal.

**Independent Test**: Run `python ingest_textbook.py` on a clean environment without LangChain. It must process markdown files and report success.

**Acceptance Scenarios**:

1. **Given** LangChain is NOT installed, **When** `python ingest_textbook.py` is executed, **Then** it processes ~20 markdown files and prints "Ingestion succeeded".
2. **Given** LangChain is NOT installed, **When** `ContentProcessor` is imported, **Then** it falls back to its built-in `RecursiveCharacterTextSplitter` and `Document` classes without error.
3. **Given** `ChunkingService` is imported without LangChain, **When** the import fails, **Then** the error is handled gracefully and does not crash the server.

---

### Edge Cases

- What happens when `OPENROUTER_API_KEY` is not set? — `LLMService` initialization logs a warning and all LLM calls return the safe fallback message.
- What happens when the OpenRouter API times out? — The HTTP call has a timeout (30 seconds); on timeout, return the safe fallback message and log the error.
- What happens when the OpenRouter model returns an empty response? — Treat it as a failure and return the safe fallback message.
- What happens when `chunking_service.py` fails to import `langchain.text_splitter`? — The import error must be caught. Since `content_processor.py` has fallback classes, the ingestion script should use `ContentProcessor` path (which already does).
- What happens when `OPENROUTER_MODEL` env var is not set? — Default to `mistralai/devstral-2512:free`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST remove all `langchain`, `langchain-openai`, `langchain-core`, and `langchain-community` packages from `requirements.txt` and all variant requirement files.
- **FR-002**: The system MUST replace the Gemini-based LLM implementation in `llm_service.py` with a direct HTTP call to the OpenRouter API (`https://openrouter.ai/api/v1/chat/completions`).
- **FR-003**: The `LLMService` class MUST preserve its existing method signatures: `__init__(api_key, model)`, `generate_response(query, context, max_tokens)`, `generate_response_with_citations(query, context)`, and `_generate_mock_response(query)`.
- **FR-004**: The system MUST read the OpenRouter API key from the `OPENROUTER_API_KEY` environment variable.
- **FR-005**: The system MUST read the model name from the `OPENROUTER_MODEL` environment variable, defaulting to `mistralai/devstral-2512:free` if not set.
- **FR-006**: The system MUST include a 30-second timeout on all HTTP calls to OpenRouter, returning the safe fallback message on timeout.
- **FR-007**: The system MUST NOT modify any files outside `requirements.txt` (and variants), `llm_service.py`, and `chunking_service.py` (import guard only).
- **FR-008**: The `content_processor.py` fallback text splitting classes MUST continue to work when LangChain is not installed.
- **FR-009**: The `chunking_service.py` LangChain import MUST be wrapped in a try/except with a fallback that prevents server crash.
- **FR-010**: The system MUST use `httpx` (already a dependency) for the OpenRouter HTTP call — no new HTTP libraries.

### Assumptions

- The existing `OPENROUTER_API_KEY` in `backend/.env` is valid and has quota for the free model.
- The `mistralai/devstral-2512:free` model is available on OpenRouter and returns responses in the standard OpenAI-compatible chat completions format.
- The `openai` Python package (used in `main.py` for the OpenAI Agent path) remains as a dependency since it is used independently from LangChain.
- `httpx` is already listed in `requirements.txt` and available.
- The `content_processor.py` built-in fallback classes are functionally sufficient for text chunking without LangChain.

### Key Entities

- **LLMService**: The service class in `llm_service.py` that wraps LLM API calls. Currently Gemini-based; will be replaced with OpenRouter HTTP calls. Consumed by `main.py` in the Gemini fallback path (when `LLM_PROVIDER` is not `openai`/`openrouter`).
- **OpenRouter Chat Completion**: The external API endpoint at `https://openrouter.ai/api/v1/chat/completions` that accepts messages in OpenAI-compatible format and returns an LLM response.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `pip install -r requirements.txt` completes with zero dependency resolution errors on Python 3.12.
- **SC-002**: `pip list | grep -i langchain` returns zero results after installation.
- **SC-003**: `python run_server.py` starts the server without any ImportError or ModuleNotFoundError.
- **SC-004**: `python ingest_textbook.py` processes all textbook files and reports "Ingestion succeeded" without LangChain installed.
- **SC-005**: A POST to `/query` with a valid textbook question returns a substantive LLM-generated answer (not the safe fallback message) when `OPENROUTER_API_KEY` is valid.
- **SC-006**: A POST to `/query` when the OpenRouter API is unreachable returns the safe fallback message within 35 seconds (30s timeout + overhead).
- **SC-007**: The `LLMService` class method signatures (`generate_response`, `generate_response_with_citations`, `_generate_mock_response`) remain unchanged.

## Scope Boundaries

### In Scope

- `backend/requirements.txt` — remove LangChain packages, add `cohere` if missing, ensure `pydantic-settings` present
- `backend/requirements_hf.txt`, `requirements_hf_optimized.txt`, `requirements_basic.txt` — remove LangChain packages
- `backend/src/services/llm_service.py` — replace Gemini implementation with OpenRouter HTTP call via `httpx`
- `backend/src/services/chunking_service.py` — add try/except import guard for `langchain.text_splitter` with fallback

### Out of Scope

- `backend/src/main.py` — no changes (OpenAI Agent path already uses `openai` package for OpenRouter)
- `backend/src/services/vector_store.py` — no changes
- `backend/src/services/embedding_service.py` — no changes
- `backend/src/services/guardrails.py` — no changes
- `backend/ingest_textbook.py` — no changes (uses `ContentProcessor` which has fallback)
- API endpoint changes — none
- Frontend changes — none
- New framework/abstraction introduction — explicitly forbidden

### Safe Fallback Message (Canonical)

```
I can only answer questions based on the Physical AI & Humanoid Robotics textbook.
```
