---
id: 5
title: Amend Constitution Debugging Hardening
stage: constitution
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: Farooque Malik
command: /sp.constitution
labels: ["constitution", "amendment", "debugging", "hardening", "security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

/sp.constitution

CONSTITUTION AMENDMENT — DEBUGGING & HARDENING PHASE
Applies ONLY to the current fixing phase.

This amendment does NOT replace or contradict Version 1.0.0.
All educational philosophy, architecture, and goals remain unchanged.

PURPOSE OF AMENDMENT:
To safely fix, stabilize, and harden the existing system
without introducing regressions or architectural drift.

RESTRICTIVE RULES (NON-NEGOTIABLE):
1. Do NOT delete, rename, or restructure any existing frontend or backend folders.
2. Do NOT modify existing API routes or frontend components unless explicitly required to fix a bug.
3. All fixes MUST be minimal, isolated, and backward-compatible.
4. Existing function signatures and return formats MUST remain unchanged.
5. Prefer adding new files (scripts, helpers) over modifying working files.
6. No mock, fake, or placeholder AI logic is allowed in production paths.

SAFETY & SECURITY RULES:
7. Never hardcode API keys, tokens, or secrets.
8. All secrets must be loaded from environment variables.
9. Add guardrails to prevent:
   - prompt injection
   - system override attempts
   - non-textbook or malicious queries

VERIFICATION REQUIREMENTS:
10. After fixes, the system MUST be verified by:
    - successful backend startup (no runtime/import errors)
    - successful frontend build (`npm run build`)
    - chatbot responding strictly from textbook content
11. If verification cannot be executed, explicitly document the exact manual steps required.

This amendment automatically expires after the fixing phase is complete.

## Response snapshot

Updated constitution from v1.0.0 to v1.1.0 (MINOR bump). Added "Amendment A: Debugging & Hardening Phase" as a new section with 11 rules organized into three categories: Restrictive Rules (A-I, 6 rules), Safety & Security Rules (A-II, 3 rules), and Verification Requirements (A-III, 2 rules). All existing v1.0.0 principles preserved unchanged. Added formal Amendment Procedure and Compliance Review subsections to Governance. Sync Impact Report embedded as HTML comment. All templates verified compatible - no updates required.

## Outcome

- Impact: Constitution amended to v1.1.0 with phase-limited debugging/hardening rules
- Tests: none
- Files: Updated .specify/memory/constitution.md
- Next prompts: Begin debugging/hardening phase following Amendment A rules
- Reflection: Amendment is additive and non-destructive; all v1.0.0 content preserved verbatim; auto-expiry clause ensures clean removal after phase ends

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS - no unresolved placeholders, version consistent, dates ISO format
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Track amendment compliance during first fix cycle
