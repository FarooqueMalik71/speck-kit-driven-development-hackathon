from typing import List, Dict, Any, Optional
import logging
import os
from .retrieval_service import RetrievalResult

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("Google Generative AI library not available. Using mock implementation.")
    GEMINI_AVAILABLE = False


class LLMService:
    """
    Service for generating AI responses using Google's Gemini API
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.model_name = model
        self.model = None

        if GEMINI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"Successfully initialized Gemini model: {model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {str(e)}")
                # Try fallback model
                try:
                    self.model = genai.GenerativeModel("gemini-1.5-pro")
                    self.model_name = "gemini-1.5-pro"
                    logger.info("Successfully initialized Gemini fallback model: gemini-1.5-pro")
                except Exception as fallback_error:
                    logger.error(f"Failed to initialize fallback model: {str(fallback_error)}")
                    self.model = None
        else:
            logger.warning("Gemini client not initialized. Using mock implementation for testing.")

    def generate_response(self, query: str, context: List[RetrievalResult], max_tokens: int = 1000) -> str:
        """
        Generate a response using the LLM based on the query and context
        """
        if self.model:
            try:
                # Prepare context from retrieval results
                context_text = ""
                if context:
                    context_text = "Relevant textbook content:\n"
                    for i, result in enumerate(context[:5]):  # Use top 5 results
                        context_text += f"\n{i+1}. {result.content[:500]}..."  # Limit content length
                        if len(result.content) > 500:
                            context_text += " [truncated]"

                # Construct the prompt
                prompt = f"""
                You are an AI assistant for the Physical AI & Humanoid Robotics textbook.
                Answer the user's question based on the provided textbook content.

                Question: {query}

                {context_text}

                Please provide a comprehensive answer based on the textbook content.
                If the information is not available in the provided context,
                politely acknowledge the limitation and suggest checking the textbook directly.
                """

                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.7,
                    ),
                )

                return response.text
            except Exception as e:
                logger.error(f"Error generating response with Gemini: {str(e)}")
                # Fallback to mock response
                return self._generate_mock_response(query)
        else:
            # Mock implementation for testing
            logger.debug(f"Using mock response generation for query: {query[:50]}...")
            return self._generate_mock_response(query)

    def _generate_mock_response(self, query: str) -> str:
        """
        Generate a mock response when Gemini is not available
        """
        return f"Based on the textbook content, here's information about: {query}. [Note: Gemini API is not available. This is a simulated response.]"

    def generate_response_with_citations(self, query: str, context: List[RetrievalResult]) -> Dict[str, Any]:
        """
        Generate a response with citations and additional metadata
        """
        response_text = self.generate_response(query, context)

        # Extract citation information from context
        citations = []
        sources = []
        for result in context:
            if result.source_file and result.source_file not in sources:
                sources.append(result.source_file)
            if result.metadata.get('section_title') and result.metadata.get('section_title') not in citations:
                citations.append(result.metadata.get('section_title', result.source_file))

        # Fallback: if no specific citations, use source files
        if not citations:
            citations = sources[:3]  # Limit to first 3 sources

        return {
            "answer": response_text,
            "citations": citations,
            "sources": sources
        }

    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate if the provided API key is working
        """
        if not GEMINI_AVAILABLE:
            return False

        try:
            genai.configure(api_key=api_key)
            test_model = genai.GenerativeModel(self.model_name)
            test_response = test_model.generate_content("Hello", generation_config=genai.types.GenerationConfig(max_output_tokens=10))
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False


if __name__ == "__main__":
    # Example usage
    import os
    api_key = os.getenv("GEMINI_API_KEY")  # Use actual key from environment for testing

    if api_key:
        service = LLMService(api_key=api_key)
        print("LLM service initialized with Gemini client")
    else:
        service = LLMService()  # Will use mock
        print("LLM service initialized with mock client")

    # Example query
    test_query = "What is Physical AI?"
    response = service.generate_response(test_query, [])
    print(f"Response: {response}")