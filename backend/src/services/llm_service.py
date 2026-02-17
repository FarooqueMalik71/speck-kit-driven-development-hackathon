from typing import List, Dict, Any, Optional
import logging
import os
import httpx
from .retrieval_service import RetrievalResult

logger = logging.getLogger(__name__)

SAFE_FALLBACK = "I can only answer questions based on the Physical AI & Humanoid Robotics textbook."
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemma-3-4b-it:free"


class LLMService:
    """Service for generating AI responses using OpenRouter API"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        # api_key param preserved for backward compat but we use OPENROUTER_API_KEY
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)
        self.client = httpx.Client(timeout=30.0)

        if self.api_key:
            logger.info(f"LLMService initialized with OpenRouter model: {self.model_name}")
        else:
            logger.warning("OPENROUTER_API_KEY not set. LLM calls will return fallback.")

    def generate_response(self, query: str, context: List[RetrievalResult], max_tokens: int = 1000) -> str:
        if not self.api_key:
            return self._generate_mock_response(query)

        context_text = ""
        if context:
            context_text = "Relevant textbook content:\n"
            for i, result in enumerate(context[:5]):
                context_text += f"\n{i+1}. {result.content[:500]}"
                if len(result.content) > 500:
                    context_text += "... [truncated]"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant for the Physical AI & Humanoid Robotics textbook. "
                    "Answer the user's question based ONLY on the provided textbook content. "
                    "If the information is not available, say so clearly."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {query}\n\n{context_text}",
            },
        ]

        try:
            response = self.client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return self._generate_mock_response(query)

    def _generate_mock_response(self, query: str) -> str:
        return SAFE_FALLBACK

    def generate_response_with_citations(self, query: str, context: List[RetrievalResult]) -> Dict[str, Any]:
        response_text = self.generate_response(query, context)

        citations = []
        sources = []
        for result in context:
            if result.source_file and result.source_file not in sources:
                sources.append(result.source_file)
            if result.metadata.get('section_title') and result.metadata.get('section_title') not in citations:
                citations.append(result.metadata.get('section_title', result.source_file))

        if not citations:
            citations = sources[:3]

        return {"answer": response_text, "citations": citations, "sources": sources}

    def validate_api_key(self, api_key: str) -> bool:
        try:
            response = httpx.post(
                OPENROUTER_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": self.model_name, "messages": [{"role": "user", "content": "test"}], "max_tokens": 5},
                timeout=10.0,
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
