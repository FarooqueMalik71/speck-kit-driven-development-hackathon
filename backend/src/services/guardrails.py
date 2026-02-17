import re
import logging

logger = logging.getLogger(__name__)

SAFE_FALLBACK = "I can only answer questions based on the Physical AI & Humanoid Robotics textbook."

# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"you\s+are\s+now\s+a",
    r"forget\s+(everything|all|your)\s+(instructions|rules|training)",
    r"override\s+(system|your)\s+(prompt|instructions|rules)",
    r"act\s+as\s+(if\s+you\s+are|a)\s+",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"do\s+not\s+follow\s+(your|the)\s+(instructions|rules)",
    r"pretend\s+(you\s+are|to\s+be)",
    r"jailbreak",
    r"DAN\s+mode",
]

TEXTBOOK_TOPICS = [
    "physical ai", "humanoid", "robot", "ros", "ros2", "gazebo",
    "isaac", "simulation", "embodied", "perception", "action",
    "control", "kinematics", "manipulation", "navigation",
    "sensor", "actuator", "motor", "vision", "language",
    "vla", "reinforcement learning", "neural", "ai", "machine learning",
    "textbook", "chapter", "book",
]


def check_query_safety(query: str) -> tuple:
    """Check if query is safe to process. Returns (is_safe, reason)."""
    query_lower = query.lower().strip()

    # Check for prompt injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query_lower):
            logger.warning(f"Prompt injection detected: {query[:80]}...")
            return False, "prompt_injection"

    # Check if query is related to textbook topics
    if len(query_lower) > 5:  # Skip very short queries
        has_topic_match = any(topic in query_lower for topic in TEXTBOOK_TOPICS)
        # Also allow general questions that could relate to the textbook
        is_question = any(query_lower.startswith(w) for w in [
            "what", "how", "why", "when", "where", "who",
            "explain", "describe", "define", "compare",
            "tell me", "can you",
        ])
        if not has_topic_match and not is_question:
            logger.info(f"Off-topic query detected: {query[:80]}...")
            return False, "off_topic"

    return True, "safe"
