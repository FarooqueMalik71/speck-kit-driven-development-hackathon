from typing import List, Dict, Any, Optional, Callable
import logging
from .retrieval_service import RetrievalService, RetrievalResult
from .hallucination_prevention import HallucinationPreventionService

logger = logging.getLogger(__name__)

class FallbackService:
    """Service for handling low-confidence AI responses with appropriate fallback mechanisms"""

    def __init__(
        self,
        retrieval_service: RetrievalService = None,
        hallucination_service: HallucinationPreventionService = None
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.hallucination_service = hallucination_service or HallucinationPreventionService()

    def handle_low_confidence_response(
        self,
        query: str,
        response: str,
        confidence_data: Dict[str, Any],
        retrieved_results: List[RetrievalResult] = None
    ) -> Dict[str, Any]:
        """Handle a low-confidence response with appropriate fallback mechanism"""
        logger.info(f"Handling low-confidence response for query: '{query[:50]}...'")

        # Determine the appropriate fallback based on confidence level
        confidence_level = confidence_data.get('confidence_level', 'very_low')
        overall_confidence = confidence_data.get('overall_confidence', 0.0)

        if overall_confidence < 0.2:
            fallback_type = 'redirect'
        elif overall_confidence < 0.4:
            fallback_type = 'acknowledge_uncertainty'
        elif overall_confidence < 0.6:
            fallback_type = 'suggest_alternatives'
        else:
            fallback_type = 'none'  # Not actually low confidence

        # Apply the appropriate fallback mechanism
        if fallback_type == 'redirect':
            result = self._redirect_to_source_content(query, retrieved_results)
        elif fallback_type == 'acknowledge_uncertainty':
            result = self._acknowledge_uncertainty(query, response, confidence_data)
        elif fallback_type == 'suggest_alternatives':
            result = self._suggest_alternatives(query, retrieved_results)
        else:
            # This shouldn't happen if called for low-confidence responses
            result = {
                'fallback_applied': False,
                'original_response': response,
                'confidence_data': confidence_data
            }

        result['fallback_type'] = fallback_type
        result['original_confidence'] = overall_confidence
        result['confidence_level'] = confidence_level

        logger.info(f"Fallback applied: {fallback_type}, confidence: {overall_confidence:.3f}")
        return result

    def _redirect_to_source_content(
        self,
        query: str,
        retrieved_results: List[RetrievalResult]
    ) -> Dict[str, Any]:
        """Redirect user to source content when confidence is very low"""
        logger.info("Applying redirect fallback - very low confidence")

        if not retrieved_results:
            message = (
                f"I'm not confident enough to answer your query '{query}' based on the available information. "
                f"Please refer to the original textbook content for accurate information."
            )
            source_list = []  # Define source_list as empty when no results
        else:
            # Create a message pointing to relevant sections
            relevant_sources = [r for r in retrieved_results if r.is_relevant][:3]  # Top 3 relevant
            source_list = []
            for result in relevant_sources:
                source_info = result.metadata.get('section', 'Unknown Section')
                source_file = result.source_file
                source_list.append(f"'{source_info}' in {source_file}")

            if source_list:
                sources_str = ", ".join(source_list)
                message = (
                    f"I'm not confident enough to answer your query '{query}' based on the available information. "
                    f"Please refer to the following sections in the textbook: {sources_str}. "
                    f"These sections contain the most relevant information to your query."
                )
            else:
                message = (
                    f"I'm not confident enough to answer your query '{query}' based on the available information. "
                    f"Please refer to the original textbook content for accurate information."
                )

        return {
            'fallback_applied': True,
            'modified_response': message,
            'suggested_action': 'consult_source',
            'redirect_info': source_list if source_list else None
        }

    def _acknowledge_uncertainty(
        self,
        query: str,
        response: str,
        confidence_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Acknowledge uncertainty while providing a limited response"""
        logger.info("Applying uncertainty acknowledgment fallback")

        explanation = confidence_data.get('confidence_explanation', 'Insufficient context')

        message = (
            f"Regarding your query '{query}', I can provide some information, but I want to be transparent about the limitations:\n\n"
            f"{response}\n\n"
            f"Note: This response has low confidence due to: {explanation}. "
            f"I recommend verifying this information in the original textbook content."
        )

        return {
            'fallback_applied': True,
            'modified_response': message,
            'suggested_action': 'verify_information',
            'confidence_explanation': explanation
        }

    def _suggest_alternatives(
        self,
        query: str,
        retrieved_results: List[RetrievalResult]
    ) -> Dict[str, Any]:
        """Suggest alternative queries or approaches when confidence is moderate"""
        logger.info("Applying alternative suggestions fallback")

        # Generate alternative queries based on retrieved content
        alternative_queries = self._generate_alternative_queries(query, retrieved_results)

        if alternative_queries:
            alternatives_str = ", ".join([f"'{q}'" for q in alternative_queries[:3]])  # Top 3
            message = (
                f"I can provide some information about '{query}', but I'm not fully confident in my response. "
                f"You might find more comprehensive information by exploring these related topics: {alternatives_str}. "
                f"Alternatively, you can refer to the specific sections in the textbook for detailed information."
            )
        else:
            message = (
                f"I can provide some information about '{query}', but I'm not fully confident in my response. "
                f"You might find more comprehensive information by referring to the specific sections in the textbook."
            )

        return {
            'fallback_applied': True,
            'modified_response': message,
            'suggested_alternatives': alternative_queries[:3],
            'suggested_action': 'explore_alternatives'
        }

    def _generate_alternative_queries(
        self,
        query: str,
        retrieved_results: List[RetrievalResult]
    ) -> List[str]:
        """Generate alternative queries based on retrieved content"""
        if not retrieved_results:
            return []

        # Extract key terms and concepts from retrieved content
        all_content = " ".join([r.content for r in retrieved_results])

        # Simple keyword extraction (in a real implementation, this could be more sophisticated)
        import re
        from collections import Counter

        # Extract words that appear frequently in the content but are not common stop words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_content.lower())
        stop_words = {
            'with', 'from', 'this', 'that', 'have', 'they', 'when', 'what', 'where', 'who', 'why', 'how',
            'will', 'would', 'could', 'should', 'than', 'then', 'some', 'said', 'each', 'which', 'their',
            'time', 'only', 'more', 'other', 'new', 'such', 'into', 'after', 'also', 'over', 'while'
        }

        word_freq = Counter(w for w in words if w not in stop_words)

        # Generate alternative queries using top keywords
        top_keywords = [word for word, _ in word_freq.most_common(10)]

        # Create alternative queries by combining keywords with the original query
        alternatives = []
        for keyword in top_keywords[:5]:
            alternatives.append(f"{keyword} in Physical AI")
            alternatives.append(f"{keyword} and robotics")

        # Remove duplicates while preserving order
        seen = set()
        unique_alternatives = []
        for alt in alternatives:
            if alt not in seen:
                seen.add(alt)
                unique_alternatives.append(alt)

        return unique_alternatives

    def apply_fallback_strategy(
        self,
        query: str,
        response: str,
        confidence_threshold: float = 0.6,
        retrieved_results: List[RetrievalResult] = None,
        confidence_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Apply fallback strategy based on confidence threshold"""
        logger.info(f"Applying fallback strategy for query with threshold {confidence_threshold}")

        # If confidence data is not provided, calculate it
        if confidence_data is None:
            confidence_data = self.retrieval_service.calculate_response_confidence(
                query, retrieved_results or [], response
            )

        overall_confidence = confidence_data.get('overall_confidence', 0.0)

        if overall_confidence < confidence_threshold:
            # Apply fallback mechanism
            fallback_result = self.handle_low_confidence_response(
                query, response, confidence_data, retrieved_results
            )

            # Update with confidence information
            fallback_result['original_response'] = response
            fallback_result['confidence_data'] = confidence_data
            fallback_result['was_below_threshold'] = True
        else:
            # Confidence is sufficient, no fallback needed
            fallback_result = {
                'fallback_applied': False,
                'modified_response': response,
                'original_response': response,
                'confidence_data': confidence_data,
                'was_below_threshold': False
            }

        return fallback_result

    def get_confidence_based_response(
        self,
        query: str,
        response: str,
        retrieved_results: List[RetrievalResult],
        confidence_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """Get a response that applies confidence-based fallbacks as needed"""
        logger.info(f"Getting confidence-based response for query: '{query[:50]}...'")

        # Calculate confidence
        confidence_data = self.retrieval_service.calculate_response_confidence(
            query, retrieved_results, response
        )

        # Apply fallback strategy
        result = self.apply_fallback_strategy(
            query, response, confidence_threshold, retrieved_results, confidence_data
        )

        # Add quality indicators
        result['response_quality'] = confidence_data.get('confidence_level', 'unknown')
        result['final_confidence'] = confidence_data.get('overall_confidence', 0.0)

        logger.info(f"Confidence-based response ready, quality: {result['response_quality']}")
        return result

# Example usage
if __name__ == "__main__":
    from .retrieval_service import RetrievalResult

    # Initialize service
    fallback_service = FallbackService()

    # Sample query and low-confidence response
    query = "What is the most advanced humanoid robot?"
    response = "The most advanced humanoid robot is the Atlas robot developed by Boston Dynamics."
    retrieved_results = [
        RetrievalResult(
            id="sample_file_0",
            content="Humanoid robots are robots with a human-like body structure, typically having a head, torso, two arms, and two legs.",
            source_file="docs/humanoid_robots.md",
            score=0.65,
            metadata={
                'chapter': '4',
                'section': 'Introduction to Humanoid Robots',
                'page_number': '45',
                'source_file': 'docs/humanoid_robots.md'
            },
            relevance_score=0.55,
            context_similarity=0.52,
            is_relevant=True
        )
    ]

    # Simulate low confidence data
    low_confidence_data = {
        'overall_confidence': 0.3,
        'retrieval_confidence': 0.4,
        'content_grounding_score': 0.25,
        'response_coherence_score': 0.45,
        'confidence_level': 'low',
        'retrieval_quality': 'low',
        'is_confident': False,
        'confidence_explanation': 'Weak retrieval results; Poorly grounded in source content'
    }

    # Test fallback mechanism
    result = fallback_service.handle_low_confidence_response(
        query, response, low_confidence_data, retrieved_results
    )
    print("Fallback Result:")
    print(f"- Fallback applied: {result['fallback_applied']}")
    print(f"- Fallback type: {result['fallback_type']}")
    print(f"- Modified response: {result['modified_response']}")
    print()

    # Test confidence-based response
    confidence_based_result = fallback_service.get_confidence_based_response(
        query, response, retrieved_results, confidence_threshold=0.6
    )
    print("Confidence-Based Result:")
    print(f"- Fallback applied: {confidence_based_result['fallback_applied']}")
    print(f"- Response quality: {confidence_based_result['response_quality']}")
    print(f"- Final confidence: {confidence_based_result['final_confidence']:.3f}")
    print(f"- Final response: {confidence_based_result['modified_response']}")