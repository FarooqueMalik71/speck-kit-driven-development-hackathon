---
id: 1
title: Create Constitution
stage: constitution
date: 2025-12-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Claude Code User
command: /sp.constitution
labels: [constitution, textbook, ai-native, robotics]
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

You are a Chief AI Architect, Robotics Systems Engineer, and Curriculum Designer
working for an AI-first university.

Your task is to generate a formal PROJECT CONSTITUTION for an AI-native technical
textbook titled:

"Physical AI & Humanoid Robotics — An AI-Native Textbook for Embodied Intelligence"

Context:
- This textbook is built using Docusaurus and deployed on GitHub/Vercel.
- It teaches Physical AI, Humanoid Robotics, ROS 2, Gazebo, NVIDIA Isaac,
  Vision-Language-Action systems, and conversational robotics.
- The book embeds AI agents (RAG chatbot, personalization, translation).
- The audience includes advanced students, engineers, and future AI founders.
- This is NOT a normal book. It is a living, AI-assisted learning system.

Instructions:
1. Write the constitution as a serious technical and academic document.
2. Do NOT write marketing language.
3. Do NOT write course content.
4. Focus on principles, constraints, philosophy, and boundaries.
5. Assume this document will be evaluated by senior AI researchers and founders.

The constitution MUST include these sections (use markdown headings):

1. Purpose
2. Educational Philosophy
3. Core Design Principles (5–7 principles)
4. Technical Constraints
5. AI Usage Policy
6. Ethical & Safety Boundaries
7. Definition of Success
8. Definition of Done

Tone & Style Requirements:
- Precise
- Professional
- Engineering-oriented
- AI-native thinking
- No fluff, no storytelling

Output Requirements:
- Output ONLY valid Markdown
- The file must be suitable to save directly as:
  /spec/constitution.md
- Do not include explanations outside the document

Generate the complete constitution now.

## Response snapshot

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

## Governance

This constitution supersedes all other development practices for the textbook project. All feature additions and modifications must align with these principles. Amendments require documentation of impact on educational objectives and approval by the academic oversight committee. All pull requests must demonstrate compliance with these principles through automated checks and human review.

**Version**: 1.0.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2025-12-15

## Outcome

- ✅ Impact: Created initial project constitution for AI-native robotics textbook
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md with complete constitution
- 🔁 Next prompts: Plan initial textbook structure and content
- 🧠 Reflection: The constitution establishes clear principles for the AI-native textbook project, focusing on simulation-first approach, AI integration, and practical robotics learning

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin textbook content development following constitution principles