<!--
SYNC IMPACT REPORT:
Version change: 1.0.0 → 1.1.0
Modified principles: None (all v1.0.0 principles preserved unchanged)
Added sections:
  - "Amendment A: Debugging & Hardening Phase" (new section with 11 rules)
  - Restrictive Rules (6 rules)
  - Safety & Security Rules (3 rules)
  - Verification Requirements (2 rules)
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ no update needed (Constitution Check section references constitution generically)
  - .specify/templates/spec-template.md: ✅ no update needed (no constitution-specific references)
  - .specify/templates/tasks-template.md: ✅ no update needed (phases remain compatible)
Follow-up TODOs:
  - Amendment A auto-expires after debugging/hardening phase completion; remove manually when phase ends
-->
# Physical AI & Humanoid Robotics — An AI-Native Textbook for Embodied Intelligence Constitution

## Purpose

This constitution establishes the governing principles for the development of an AI-native technical textbook that serves as a living, AI-assisted learning system for embodied intelligence. The textbook integrates Physical AI, Humanoid Robotics, ROS 2, Gazebo, NVIDIA Isaac, Vision-Language-Action systems, and conversational robotics into a comprehensive educational platform for advanced students, engineers, and future AI founders.

## Educational Philosophy

Learning in embodied intelligence requires active engagement with complex systems. The textbook must facilitate hands-on experimentation, simulation-based learning, and iterative understanding of physical AI concepts. The educational approach prioritizes practical implementation over theoretical exposition, with AI agents providing personalized learning paths and real-time assistance to accommodate diverse learning styles and technical backgrounds.

## Core Design Principles

### I. Simulation-First Architecture
All robotics concepts must be demonstrable through simulation environments before theoretical exposition. Every chapter includes executable Gazebo/Isaac simulations with reproducible results. This ensures learners can validate concepts in controlled environments before advancing to hardware implementations.

### II. AI-Native Learning Interface
The textbook embeds RAG chatbots, personalization engines, and translation systems as core components rather than supplementary features. All content must be structured for AI consumption and generation, enabling dynamic adaptation to learner needs and real-time content updates.

### III. Multi-Modal Interaction (NON-NEGOTIABLE)
All educational content must support text, visual, and interactive modalities. Every concept requires corresponding visualizations, code examples, and interactive elements. Learning pathways must accommodate both sequential reading and exploratory discovery patterns.

### IV. ROS 2 Integration Standard
All robotics examples and exercises must utilize ROS 2 architecture patterns. Message types, node structures, and communication protocols must align with current ROS 2 best practices. This ensures learners develop industry-relevant skills and can transition directly to professional robotics development.

### V. Hardware-Abstracted Learning
All concepts must be teachable through simulation before hardware deployment. Code examples must support both simulated and real hardware execution with minimal configuration changes. This enables broad accessibility while maintaining practical applicability.

### VI. Vision-Language-Action Integration
All robotics content must incorporate perception-action loops with visual processing, natural language understanding, and motor control. This reflects the reality of modern embodied AI systems and prepares learners for current industry practices.

### VII. Conversational Robotics Foundation
The textbook must demonstrate how to build systems that interact naturally with humans through speech, gesture, and contextual understanding. This includes integration of large language models with robotic control systems.

## Technical Constraints

The textbook uses Docusaurus as the documentation framework with GitHub/Vercel deployment. All embedded AI agents must operate within reasonable computational constraints for student access. Code examples must be compatible with standard ROS 2 distributions (Humble Hawksbill or later). All simulations must run in Docker containers for reproducibility. The system must support multi-language translation with consistent technical terminology across languages.

## AI Usage Policy

AI agents within the textbook must be transparent about their capabilities and limitations. Generated content requires human verification for technical accuracy. Personalization algorithms must respect learner privacy and not create filter bubbles that limit exposure to fundamental concepts. AI assistance must enhance rather than replace critical thinking and problem-solving skills.

## Ethical & Safety Boundaries

All robotics examples must include safety considerations and risk assessments. Content must address ethical implications of autonomous systems and embodied AI. The textbook must include discussions of responsible AI deployment and potential societal impacts. Code examples must include safety checks and fail-safes where applicable.

## Definition of Success

Success is measured by learner ability to implement working robotics systems after completing textbook modules. Students must demonstrate proficiency in ROS 2, simulation environments, and vision-language-action integration. The AI assistance features must measurably improve learning outcomes compared to traditional textbooks. The system must support diverse learning styles and technical backgrounds effectively.

## Definition of Done

The textbook is complete when all core robotics concepts are covered with simulation examples, AI assistance is fully integrated and responsive, multi-language support is functional, and all code examples are tested and verified. The system must be deployed and accessible through standard web browsers with offline capabilities for core content.

---

## Amendment A: Debugging & Hardening Phase

**Status**: ACTIVE | **Adopted**: 2026-02-15 | **Scope**: Current fixing phase only

This amendment applies ONLY to the current debugging and hardening phase. It does NOT replace or contradict any principle in Version 1.0.0. All educational philosophy, architecture, and goals remain unchanged. This amendment automatically expires after the fixing phase is complete.

### Purpose of Amendment

To safely fix, stabilize, and harden the existing system without introducing regressions or architectural drift.

### A-I. Restrictive Rules (NON-NEGOTIABLE)

1. **No Structural Changes**: Do NOT delete, rename, or restructure any existing frontend or backend folders.
2. **No Route Modifications**: Do NOT modify existing API routes or frontend components unless explicitly required to fix a bug.
3. **Minimal Isolated Fixes**: All fixes MUST be minimal, isolated, and backward-compatible.
4. **Signature Preservation**: Existing function signatures and return formats MUST remain unchanged.
5. **Additive Preference**: Prefer adding new files (scripts, helpers) over modifying working files.
6. **No Mock Logic in Production**: No mock, fake, or placeholder AI logic is allowed in production paths.

### A-II. Safety & Security Rules

7. **No Hardcoded Secrets**: Never hardcode API keys, tokens, or secrets in source code.
8. **Environment-Only Secrets**: All secrets MUST be loaded from environment variables.
9. **Input Guardrails**: Add guardrails to prevent:
   - Prompt injection attacks
   - System override attempts
   - Non-textbook or malicious queries

### A-III. Verification Requirements

10. **Post-Fix Verification**: After fixes, the system MUST be verified by:
    - Successful backend startup (no runtime/import errors)
    - Successful frontend build (`npm run build`)
    - Chatbot responding strictly from textbook content
11. **Manual Step Documentation**: If verification cannot be executed automatically, explicitly document the exact manual steps required.

### Amendment Expiry

This amendment automatically expires after the fixing phase is complete. Upon expiry, remove this section and bump the version to the next appropriate release.

---

## Governance

This constitution supersedes all other development practices for the textbook project. All feature additions and modifications must align with these principles. Amendments require documentation of impact on educational objectives and approval by the academic oversight committee. All pull requests must demonstrate compliance with these principles through automated checks and human review.

### Amendment Procedure

1. Amendments MUST state their scope (permanent or phase-limited).
2. Phase-limited amendments MUST include an expiry condition.
3. Amendments MUST NOT contradict existing core principles; they MAY add constraints.
4. Version increments follow semantic versioning:
   - MAJOR: Backward-incompatible principle removals or redefinitions.
   - MINOR: New principle/section added or materially expanded guidance.
   - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
5. All amendments MUST be documented with a Sync Impact Report.

### Compliance Review

All code changes during an active amendment period MUST be checked against both the core principles and any active amendments. Violations of amendment rules are treated with the same severity as core principle violations.

**Version**: 1.1.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2026-02-15
