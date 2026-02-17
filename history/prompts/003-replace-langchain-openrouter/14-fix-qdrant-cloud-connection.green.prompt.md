---
id: 14
title: Fix Qdrant Cloud Connection
stage: green
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: 003-replace-langchain-openrouter
branch: 003-replace-langchain-openrouter
user: farooque_malik
command: implement plan
labels: ["qdrant", "bugfix", "connection", "port"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/vector_store.py
tests:
  - Manual: start backend and verify "Successfully connected to Qdrant" in logs
  - Manual: POST /query returns textbook-grounded answer with sources
---

## Prompt

Implement the following plan:

# Fix Qdrant Cloud Connection

The backend server logs show:
```
Could not connect to Qdrant: Unexpected Response: 404 (Not Found)
Raw response content: b'404 page not found\n'
```

Root cause: `QDRANT_HOST` in `.env` is `https://019f480a-...cloud.qdrant.io` — missing port `:6333`. When `QdrantClient(url=...)` is called without a port, the request goes to the default HTTPS port 443, which returns a 404. Qdrant Cloud REST API listens on port 6333.

Fix: Modify cloud URL construction in `vector_store.py` to append `:6333` when no port is present.

## Response snapshot

Applied a 3-line addition to `backend/src/services/vector_store.py` (lines 43-46). After constructing the `cloud_url` with `https://` prefix, the code now splits on `//` and checks if the host portion contains a colon (port separator). If no port is found, it appends `:6333`. This ensures the QdrantClient connects to the correct REST API port on Qdrant Cloud.

## Outcome

- ✅ Impact: Fixes Qdrant Cloud 404 error, enables real RAG retrieval instead of mock fallback
- 🧪 Tests: Manual verification — check server logs and POST /query endpoint
- 📁 Files: 1 file modified (backend/src/services/vector_store.py)
- 🔁 Next prompts: Verify end-to-end with live Qdrant Cloud, run ingestion if collection is empty
- 🧠 Reflection: Qdrant Cloud REST API uses port 6333 even over HTTPS; the python client doesn't auto-detect this

## Evaluation notes (flywheel)

- Failure modes observed: Missing port causes 443 default, Qdrant returns 404, silent fallback to mock mode
- Graders run and results (PASS/FAIL): N/A — manual verification required
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider also supporting gRPC port 6334 if prefer_grpc is ever enabled
