from typing import List, Dict, Any, Optional, Tuple
import logging
import re
from .retrieval_service import RetrievalService
from .embedding_service import EmbeddingService
from .vector_store import VectorStoreService

logger = logging.getLogger(__name__)

class HallucinationPreventionService:
    """Service for detecting and preventing AI hallucinations in responses"""

    def __init__(self, retrieval_service: RetrievalService = None, embedding_service: EmbeddingService = None):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.embedding_service = embedding_service or EmbeddingService()

    def detect_hallucinations(self, query: str, response: str, retrieved_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potential hallucinations in AI response based on provided context"""
        logger.info(f"Detecting hallucinations for query: '{query[:50]}...'")

        try:
            # 1. Check factual consistency with retrieved context
            factual_consistency_score = self._check_factual_consistency(response, retrieved_context)

            # 2. Check for unsupported claims
            unsupported_claims = self._identify_unsupported_claims(response, retrieved_context)

            # 3. Check for overconfidence in uncertain statements
            confidence_indicators = self._check_overconfidence_indicators(response)

            # 4. Check for contradiction with context
            contradictions = self._check_contradictions(response, retrieved_context)

            # 5. Calculate hallucination probability
            hallucination_probability = self._calculate_hallucination_probability(
                factual_consistency_score,
                len(unsupported_claims),
                len(contradictions),
                confidence_indicators
            )

            result = {
                'hallucination_probability': hallucination_probability,
                'factual_consistency_score': factual_consistency_score,
                'unsupported_claims': unsupported_claims,
                'contradictions': contradictions,
                'confidence_indicators': confidence_indicators,
                'is_hallucinated': hallucination_probability > 0.5,  # Threshold for hallucination
                'safety_level': self._determine_safety_level(hallucination_probability),
                'recommendation': self._generate_recommendation(hallucination_probability, unsupported_claims)
            }

            logger.info(f"Hallucination detection result: probability={result['hallucination_probability']:.3f}, is_hallucinated={result['is_hallucinated']}")
            return result

        except Exception as e:
            logger.error(f"Error in hallucination detection: {str(e)}")
            return {
                'hallucination_probability': 1.0,
                'factual_consistency_score': 0.0,
                'unsupported_claims': [],
                'contradictions': [],
                'confidence_indicators': [],
                'is_hallucinated': True,
                'safety_level': 'unsafe',
                'recommendation': 'Reject response due to error in hallucination detection'
            }

    def _check_factual_consistency(self, response: str, retrieved_context: List[Dict[str, Any]]) -> float:
        """Check how consistent the response is with the retrieved context"""
        if not retrieved_context:
            return 0.0

        try:
            # Calculate similarity between response and context
            response_embedding = self.embedding_service.generate_embedding(response)
            context_similarities = []

            for context_item in retrieved_context:
                context_content = context_item.get('content', '')
                if context_content:
                    context_embedding = self.embedding_service.generate_embedding(context_content[:1000])

                    import numpy as np
                    response_array = np.array(response_embedding)
                    context_array = np.array(context_embedding)

                    # Calculate cosine similarity
                    similarity = np.dot(response_array, context_array) / (
                        np.linalg.norm(response_array) * np.linalg.norm(context_array)
                    )
                    context_similarities.append(float(similarity))

            if context_similarities:
                avg_similarity = sum(context_similarities) / len(context_similarities)
                return avg_similarity
            else:
                return 0.0

        except Exception as e:
            logger.warning(f"Error in factual consistency check: {str(e)}")
            return 0.0

    def _identify_unsupported_claims(self, response: str, retrieved_context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify claims in the response that are not supported by the context"""
        claims = self._extract_claims(response)
        unsupported_claims = []

        context_text = " ".join([item.get('content', '') for item in retrieved_context])

        for claim in claims:
            # Check if claim is supported by context
            is_supported = self._is_claim_supported(claim, context_text)
            if not is_supported:
                unsupported_claims.append({
                    'claim': claim,
                    'is_supported': False,
                    'confidence': 0.0
                })

        return unsupported_claims

    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        # Look for statements that make claims about facts
        claim_patterns = [
            r'\b(?:is|was|are|were|has|have|had|will|would|can|could|should|must)\s+\w+',
            r'\b(?:states that|indicates that|shows that|proves that|demonstrates that)\s+[^.!?]*',
            r'\b(?:according to|based on|derived from)\s+\w+',
            r'\b(?:research shows|studies indicate|data suggests)\s+[^.!?]*',
        ]

        claims = []
        for pattern in claim_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            claims.extend(matches)

        # Also extract sentences that contain numbers, dates, or specific technical terms
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if (re.search(r'\d+', sentence) or  # Contains numbers
                re.search(r'\b(?:the|a|an)\s+\w+ing\b', sentence) or  # Contains technical terms
                len(sentence.split()) > 3):  # At least 4 words
                claims.append(sentence)

        return list(set(claims))  # Remove duplicates

    def _is_claim_supported(self, claim: str, context: str) -> bool:
        """Check if a claim is supported by the context"""
        try:
            claim_embedding = self.embedding_service.generate_embedding(claim)
            context_embedding = self.embedding_service.generate_embedding(context[:1000])

            import numpy as np
            claim_array = np.array(claim_embedding)
            context_array = np.array(context_embedding)

            # Calculate cosine similarity
            similarity = np.dot(claim_array, context_array) / (
                np.linalg.norm(claim_array) * np.linalg.norm(context_array)
            )

            # If similarity is above threshold, consider claim supported
            return float(similarity) > 0.3

        except Exception as e:
            logger.warning(f"Error checking claim support: {str(e)}")
            # Fallback: check for keyword overlap
            claim_words = set(claim.lower().split())
            context_words = set(context.lower().split())
            overlap = claim_words.intersection(context_words)
            return len(overlap) / len(claim_words) if claim_words else 0 > 0.3

    def _check_overconfidence_indicators(self, response: str) -> List[str]:
        """Check for overconfidence indicators in the response"""
        overconfidence_patterns = [
            r'\babsolutely certain\b',
            r'\bdefinitely\b',
            r'\bfor sure\b',
            r'\bwithout doubt\b',
            r'\bclearly\b',
            r'\bobviously\b',
            r'\bcertainly\b',
            r'\bundoubtedly\b',
            r'\bwithout question\b',
            r'\bcan confirm\b'
        ]

        indicators = []
        for pattern in overconfidence_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            indicators.extend(matches)

        return list(set(indicators))  # Remove duplicates

    def _check_contradictions(self, response: str, retrieved_context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for contradictions between response and context"""
        contradictions = []

        for context_item in retrieved_context:
            context_content = context_item.get('content', '')
            if context_content:
                # Look for contradictory language patterns
                contradiction_indicators = self._find_contradictions(response, context_content)
                if contradiction_indicators:
                    contradictions.append({
                        'context_snippet': context_content[:200],
                        'contradiction_indicators': contradiction_indicators,
                        'confidence': 0.5  # Default confidence
                    })

        return contradictions

    def _find_contradictions(self, response: str, context: str) -> List[str]:
        """Find potential contradictions between response and context"""
        contradiction_patterns = [
            r'\bnot\s+\w+',
            r'\bnever\s+\w+',
            r'\bdoes not',
            r'\bno\s+\w+',
            r'\bincorrect',
            r'\bfalse',
            r'\bwrong',
            r'\bdisagree',
        ]

        contradictions = []

        # Check for direct contradictions
        for pattern in contradiction_patterns:
            response_matches = re.findall(pattern, response, re.IGNORECASE)
            context_matches = re.findall(pattern, context, re.IGNORECASE)

            # If response contradicts what's in context
            if response_matches and context_matches:
                contradictions.extend(response_matches)

        return list(set(contradictions))

    def _calculate_hallucination_probability(
        self,
        factual_consistency_score: float,
        unsupported_claim_count: int,
        contradiction_count: int,
        confidence_indicators: List[str]
    ) -> float:
        """Calculate overall hallucination probability based on multiple factors"""
        # Base probability starts low
        prob = 0.1

        # Increase probability if factual consistency is low
        if factual_consistency_score < 0.3:
            prob += (0.3 - factual_consistency_score) * 2

        # Increase probability with unsupported claims
        prob += min(unsupported_claim_count * 0.2, 0.5)  # Cap at 0.5

        # Increase probability with contradictions
        prob += min(contradiction_count * 0.3, 0.4)  # Cap at 0.4

        # Increase probability if there are overconfidence indicators with low consistency
        if confidence_indicators and factual_consistency_score < 0.4:
            prob += 0.2

        # Ensure probability is between 0 and 1
        return min(max(prob, 0.0), 1.0)

    def _determine_safety_level(self, hallucination_probability: float) -> str:
        """Determine safety level based on hallucination probability"""
        if hallucination_probability < 0.3:
            return 'safe'
        elif hallucination_probability < 0.6:
            return 'moderate'
        elif hallucination_probability < 0.8:
            return 'caution'
        else:
            return 'unsafe'

    def _generate_recommendation(self, hallucination_probability: float, unsupported_claims: List[Dict[str, Any]]) -> str:
        """Generate recommendation based on hallucination analysis"""
        if hallucination_probability > 0.8:
            return 'Reject response - high hallucination probability'
        elif hallucination_probability > 0.6:
            return 'Fact-check required - potential hallucinations detected'
        elif hallucination_probability > 0.4:
            return 'Review response - some unsupported claims detected'
        else:
            return 'Response appears to be grounded in context'

    def prevent_hallucinations(self, query: str, response: str, retrieved_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive hallucination prevention that modifies response if needed"""
        detection_result = self.detect_hallucinations(query, response, retrieved_context)

        if detection_result['is_hallucinated']:
            # Generate a safer response that acknowledges limitations
            safe_response = self._generate_safe_response(query, retrieved_context, detection_result)
            detection_result['modified_response'] = safe_response
            detection_result['response_modified'] = True
        else:
            detection_result['response_modified'] = False
            detection_result['modified_response'] = response

        return detection_result

    def _generate_safe_response(self, query: str, retrieved_context: List[Dict[str, Any]], detection_result: Dict[str, Any]) -> str:
        """Generate a safe response when hallucinations are detected"""
        if not retrieved_context:
            return f"I cannot provide a definitive answer to '{query}' as I don't have sufficient context from the textbook."

        # Create a response that acknowledges limitations
        context_snippets = [item.get('content', '')[:200] for item in retrieved_context[:2]]
        context_preview = " ".join(context_snippets)

        safe_response = (
            f"Based on the provided context, I can share information related to your query: '{query}'. "
            f"However, please note that the specific details may be limited to the following: {context_preview}... "
            f"If you need more comprehensive information, I recommend checking the original textbook content."
        )

        return safe_response

# Example usage
if __name__ == "__main__":
    # Initialize service
    prevention_service = HallucinationPreventionService()

    # Sample query and response
    query = "What is the main principle of Physical AI?"
    response = "Physical AI is a completely new field that was invented in 2023 by researchers at a fictional university. It has absolutely no relation to traditional AI and represents a revolutionary breakthrough that changes everything."

    # Sample retrieved context
    retrieved_context = [
        {
            'content': "Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments. Unlike traditional AI that operates primarily in digital spaces, Physical AI systems must understand and interact with the physical world through sensors and actuators.",
            'source_file': 'introduction.md',
            'score': 0.85
        }
    ]

    # Test hallucination detection
    result = prevention_service.detect_hallucinations(query, response, retrieved_context)
    print(f"Hallucination detection result: {result}")

    # Test hallucination prevention
    prevention_result = prevention_service.prevent_hallucinations(query, response, retrieved_context)
    print(f"Prevention result: {prevention_result}")